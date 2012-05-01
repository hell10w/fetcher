# -*- coding: utf-8 -*-

from queues import get_tasks_queue
from fetcher.response import Response


class Task(object):
    '''Отдельная задача'''

    def __init__(self, **kwarg):
        self.response = Response()
        self.setup(**kwarg)

    def setup(self, **kwarg):
        for name, value in kwarg.iteritems():
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

        self._queue = get_tasks_queue(**kwargs)

    def add_task(self, task=None, **kwargs):
        '''
        Добавляет задачу в очередь.
        Если нужно, создает её по параметрам или устанавливает дополнительные
        параметры к существующей
        '''

        if len(kwargs) and task:
            for name, value in kwargs.iteritems():
                setattr(task, name, value)
        if not task:
            task = Task(**kwargs)

        priority = getattr(task, 'priority', 100)
        self._queue.put((priority, task))

    def get_task(self):
        '''Извлекает задачу'''
        return self._queue.get()

    def empty(self):
        '''Проверяет пустоту очереди'''
        return self._queue.empty()
