# -*- coding: utf-8 -*-

from fetcher.tasks import Task, Tasks, MemoryQueue, MongoQueue
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

                for finished_task in self.dispatcher.finished_tasks():
                    self._process_finished_task(finished_task)

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

    def tasks_collector(self, task):
        yield None

    def _process_finished_task(self, task):
        '''Передача управление обработчику для каждого завершенного task'''
        if not task:
            return
        handler = getattr(task, 'handler', None)
        if not handler:
            self._process_for_tasks(self.tasks_collector(task))
        else:
            if type(handler) == str:
                handler = getattr(self, 'task_%s' % handler, None)
            if callable(handler):
                self._process_for_tasks(handler(task))

    def _process_for_tasks(self, generator):
        '''Извлекает и добавляет в очередь задания из функции'''
        if not generator:
            return
        for task in generator() if callable(generator) else generator:
            if isinstance(task, Task):
                self.tasks.add_task(task)
