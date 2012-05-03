# -*- coding: utf-8 -*-

from tasks import Task, Tasks
from dispatchers import get_tasks_manager


class MultiFetcher(object):
    '''
    Менеджер асинхроной работы

    О захламлении памяти можно не беспокоиться потому что:
        - очередь на основе mongodb может быть любого размера, она
            хранится в дисковом пространстве
        - ответ на каждый запрос скачивается во временный файл через
            буфер размером 10КБ
    '''

    def __init__(self, **kwargs):
        '''
        Конструктор менеджера асинхроной работы.
        Параметры:
            fetcher_transport - Транспорт для запросов
            dispatcher_type - Тип диспетчера задач
            queue_transport - Вид размещения очереди задач
        '''
        #настройка диспетчера задач
        self.dispatcher = get_tasks_manager(**kwargs)
        #создание очереди заданий
        self.tasks = Tasks(**kwargs)

    def start(self):
        '''Стартует работу менеджера'''

        self._should_stop = False

        while not self._should_stop:
            while not self.dispatcher.is_full() and not self.tasks.empty():
                _, task = self.tasks.get_task()
                self.dispatcher.process_task(task)

            if self.dispatcher.is_empty():
                break

            self.dispatcher.wait_available()

            for finished_task in self.dispatcher.finished_tasks():
                self._process_finished_task(finished_task)

            self._process_for_tasks(self.tasks_generator)

    def stop(self):
        '''Останавливает работу менеджера'''
        self._should_stop = True


    def tasks_generator(self):
        '''Генератор задач выполняемый при каждом выполнении хотя бы одной задачи'''
        yield None

    def _process_finished_task(self, task):
        '''Передача управление обработчику для каждого завершенного task'''
        handler = getattr(task, 'handler', None)
        if handler:
            if type(handler) == str:
                handler = getattr(self, 'task_%s' % handler, None)
            if callable(handler):
                self._process_for_tasks(handler(task))

    def _process_for_tasks(self, generator):
        '''Извлекает и добавляет в очередь задания из функции'''
        if not generator:
            return
        for task in generator():
            if isinstance(task, Task):
                self.tasks.add_task(task)
