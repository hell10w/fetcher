# -*- coding: utf-8 -*-

from queues import MemoryQueue, MongoQueue
from fetcher.queries import Request, Response


class Task(object):
    '''Отдельная задача'''

    def __init__(self, **kwarg):
        self.response = Response()
        self.request = Request()
        self.setup(**kwarg)

    def setup(self, **kwarg):
        for name, value in kwarg.iteritems():
            if hasattr(self.request, name):
                setattr(self.request, name, value)
            else:
                setattr(self, name, value)

    def process_response(self):
        # TODO: здесь нужно присовокупить все нужные параметры
        # из ответа, такие как куки, к Таску, в зависимости от
        # настроек
        pass


class Tasks(object):
    '''Менеджер задач'''

    def __init__(self, **kwargs):
        '''
        Конструктор менеджера задач.
        Параметры:
            tasks_container - тип контейнера для хранения задач.
                Может принимать следующие значения: memory, mongo
        '''

        self._queue = kwargs.pop('queue', MongoQueue)(**kwargs)

    def add_task(self, task=None, **kwargs):
        '''
        Добавляет задачу в очередь.
        Если нужно, создает её по параметрам или устанавливает дополнительные
        параметры к существующей
        '''

        priority = kwargs.pop('priority', None) or \
                   getattr(task, 'priority', None) or \
                   100

        if len(kwargs) and task:
            for name, value in kwargs.iteritems():
                setattr(task, name, value)
        if not task:
            task = Task(**kwargs)

        self._queue.put((priority, task))

    def size(self):
        '''Размер очереди задач'''
        return self._queue.qsize()

    def get_task(self):
        '''Извлекает задачу'''
        return self._queue.get()

    def empty(self):
        '''Проверяет пустоту очереди'''
        return self._queue.empty()
