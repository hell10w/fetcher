# -*- coding: utf-8 -*-

from fetcher.tasks import Task, TaskResult, TasksGroup, Tasks
from fetcher.multifetch.dispatcher import Dispatcher


class MultiFetcher(object):
    '''Менеджер асинхроной работы'''

    # имя паука - для отображения в админке. по-умолчанию - имя класса
    name = None

    def __init__(self, **kwargs):
        '''
        Конструктор менеджера асинхроной работы.
        Параметры:
            queue_transport - Контейнер задач
        '''
        self.dispatcher = Dispatcher(**kwargs)
        self.tasks = Tasks(**kwargs)

        self.restart_tasks_generator(generator=self.tasks_generator())

    def start(self):
        '''Стартует работу менеджера'''

        self._process_for_tasks(self.on_start())

        try:
            self._should_stop = False

            self._process_for_tasks(self._process_tasks_generator)

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

                self._process_for_tasks(self._process_tasks_generator)

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

    def _process_tasks_generator(self):
        '''Генерация задач если генератор включен'''
        if self.tasks_generator_enabled:
            try:
                while not self.tasks.full():
                    yield self.tasks_generator_object.next()
            except StopIteration:
                self.tasks_generator_enabled = False

    def restart_tasks_generator(self, generator):
        '''Перезапуск генератора задач'''
        self.tasks_generator_object = generator
        self.tasks_generator_enabled = True

    def groups_collector(self, group):
        '''Сюда стекаются все выполненные группы у которых нет обработчиков'''
        yield None

    def tasks_collector(self, task, error=None):
        '''Сюда стекаются все выполненные задачи у которых нет обработчиков'''
        yield None

    def task_group(self, task, error=None):
        '''Внутренний обработчик загрузки зачади ищ группы'''
        # получаем группы
        group = TasksGroup.groups.get(task.group, None)
        # запоминаем выполненную задачу в группу
        group.finished_tasks[task.index] = task
        if error:
            group.errors[task.index] = error
        # уменьшаем счетчик оставшихся задач
        group.count -= 1
        # если все задачи выполнены -
        if not group.count:
            # сворачиваем в словарь все выполненные задачи: url задачи - выполненная задача
            # url устанавливается старый (при выполнении мог быть редирект, так вот, там он
            # тот, который установили при создании группы
            group.finished_tasks = [
                TaskResult(task=task, error=error)
                for task, error in zip(group.finished_tasks, group.errors)
            ]
            group.finished_tasks = zip(
                group.urls,
                group.finished_tasks
            )
            group.finished_tasks = dict(group.finished_tasks)
            # выполнение обработчика группы - и генерация задач/групп
            handler = getattr(group, 'handler', self.groups_collector)
            if type(handler) == str:
                handler = getattr(self, 'group_%s' % handler, None)
            if callable(handler):
                self._process_for_tasks(handler(group))

    def _process_finished_task(self, task, error=None):
        '''Передача управление обработчику для каждого завершенного task'''
        if not task:
            return

        args = [task]
        if error:
            args.append(error)

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
                self.tasks.add_group(task)
