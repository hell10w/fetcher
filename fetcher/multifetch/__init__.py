# -*- coding: utf-8 -*-

from fetcher.tasks import Task, TasksGroup, Tasks, MemoryQueue, MongoQueue
from fetcher.fetch import Request
from fetcher.multifetch.dispatcher import Dispatcher


class MultiFetcher(object):
    '''
    Менеджер асинхроной работы

    О захламлении памяти можно не беспокоиться потому что:
        - очередь на основе mongodb может быть любого размера, она
            хранится в дисковом пространстве
        - ответ на каждый запрос скачивается во временный файл
    '''

    def __init__(self, **kwargs):
        '''
        Конструктор менеджера асинхроной работы.
        Параметры:
            queue_transport - Контейнер задач
        '''
        self.dispatcher = Dispatcher(**kwargs)
        self.tasks = Tasks(**kwargs)

    def start(self):
        '''Стартует работу менеджера'''

        self.on_start()

        try:
            self._should_stop = False

            self._process_for_tasks(self.tasks_generator)

            while not self._should_stop:
                while not self.dispatcher.is_full() and not self.tasks.empty():
                    _, task = self.tasks.get_task()
                    if task:
                        self.dispatcher.process_task(task)

                if self.dispatcher.is_empty():
                    break

                self.dispatcher.wait_available()

                for finished_task, error in self.dispatcher.finished_tasks():
                    self._process_finished_task(finished_task, error)

                self._process_for_tasks(self.tasks_generator)

                self.on_loop()

        except KeyboardInterrupt:
            pass

        self.on_stop()

    def stop(self):
        '''Останавливает работу менеджера'''
        self._should_stop = True

    def on_start(self):
        '''Вызывается перед началом работы'''
        pass

    def on_stop(self):
        '''Вызывается по завершении работы'''
        pass

    def on_loop(self):
        '''Вызывается на каждом проходе цикла'''
        pass

    def tasks_generator(self):
        '''Генератор задач выполняемый при каждом выполнении хотя бы одной задачи'''
        yield None

    def groups_collector(self, group):
        yield None

    def tasks_collector(self, task):
        yield None

    def tasks_errors_collector(self, task, error):
        yield None

    '''def task__script_loaded(self, task):
        old_task = task.old_task
        old_task.remote_scripts[task.script_index] = task.response.get_body()
        old_task.remote_scripts_count -= 1

        if not old_task.remote_scripts_count:
            scripts = old_task.xpath_list('//script[@src]')
            #print scripts
            for index, script in enumerate(scripts):
                #print old_task.remote_scripts[index]
                #print '-' * 50
                old_task.html_replace(
                    script,
                    '<script>' + old_task.remote_scripts[index] + '</script>'
                )
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            #print old_task.html_content()
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            old_task.response.body = old_task.html_content()
            self._process_finished_task(old_task)

    def get_scripts_load_generator(self, task):
        task.html_tree.make_links_absolute(task.response.url)

        remote_scripts = task.xpath_list('//script[@src]/@src')

        if remote_scripts:
            task.remote_scripts_count = len(remote_scripts)
            task.remote_scripts=[None for _ in range(task.remote_scripts_count)]

            def generator():
                for index, src in enumerate(remote_scripts):
                    yield Task(
                        url=src,
                        cookies=task.request.cookies,
                        script_index=index,
                        handler='_script_loaded',
                        old_task=task
                    )

            return generator

        return None'''

    def task_group(self, task, error=None):
        group = task.group

        group.finished_tasks[task.index] = task
        group.count -= 1

        if not group.count:
            group.finished_tasks = zip(
                group.urls,
                group.finished_tasks
            )
            group.finished_tasks = dict(group.finished_tasks)

            handler = getattr(group, 'handler', self.groups_collector)
            if type(handler) == str:
                handler = getattr(self, 'group_%s' % handler, None)
            if callable(handler):
                self._process_for_tasks(handler(group))

    def _process_finished_task(self, task, error=None):
        '''Передача управление обработчику для каждого завершенного task'''
        if not task:
            return

        #handler = None
        args = [task]

        '''if getattr(task, 'load_scripts', False):
            generator = self.get_scripts_load_generator(task)
            if generator:
                handler = generator
                args = []'''

        #if not handler:
        if error:
            handler = getattr(task, 'error_handler', self.tasks_errors_collector)
            args.append(error)
        else:
            handler = getattr(task, 'handler', self.tasks_collector)

        if type(handler) == str:
            handler = getattr(self, 'task_%s' % handler, None)
        if callable(handler):
            self._process_for_tasks(handler(*args))

    def _process_for_tasks(self, generator):
        '''Извлекает и добавляет в очередь задания из функции'''
        if not generator:
            return
        for task in generator() if callable(generator) else generator:
            if isinstance(task, Task):
                self.tasks.add_task(task)
            elif isinstance(task, TasksGroup):
                self._process_for_tasks(task.produce_tasks)
