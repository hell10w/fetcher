# -*- coding: utf-8 -*-

from fetcher.tasks.queues import MemoryQueue, MongoQueue
from fetcher.fetch import Extensions, Response, Request


class Task(Extensions):
    '''Отдельная задача'''

    def __init__(self, **kwarg):
        self.response = Response()
        self.request = Request()
        self.setup(**kwarg)

    def setup(self, **kwarg):
        '''Настройка параметров'''
        for name, value in kwarg.iteritems():
            if hasattr(self.request, name):
                setattr(self.request, name, value)
            else:
                setattr(self, name, value)

    def clone(self):
        '''Возвращает копию таска'''
        kargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key.startswith('_')
        )
        return Task(**kargs)

    def process_response(self):
        '''Подготовка будущего запроса исходя из ответа'''
        self.request.url = self.response.url
        self.request.cookies.update(self.response.cookies)


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

        if task:
            task = task.clone()

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
