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
            if isinstance(value, Response):
                self.response = value.clone()
                continue
            if isinstance(value, Request):
                self.request = value.clone()
                continue
            if hasattr(self.request, name):
                setattr(self.request, name, value)
            else:
                setattr(self, name, value)
        return self

    def clone(self, **kwargs):
        '''Возвращает копию таска'''
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key.startswith('_')
        )
        return Task(**_kwargs).setup(**kwargs)

    def process_response(self):
        '''Подготовка будущего запроса исходя из ответа'''
        self.request.url = self.response.url
        self.request.cookies.update(self.response.cookies)
        self.request.post = None
        self.request.is_multipart_post = False


class TaskResult(dict):
    def __getattr__(self, name):
        return self[name]


class TasksGroup(object):
    '''Группа задач'''

    groups = {}

    def __init__(self, task, urls, **kwarg):
        TasksGroup.groups[id(self)] = self

        self.task = task
        self.count = len(urls)
        self.urls = urls
        self.errors = [None] * self.count
        self.finished_tasks = [None] * self.count
        self.setup(**kwarg)

    def __del__(self):
        TasksGroup.groups.pop(id(self), None)

    def setup(self, **kwarg):
        '''Настройка параметров'''
        for name, value in kwarg.iteritems():
            setattr(self, name, value)

    def produce_tasks(self):
        '''Генератор задач '''
        for index, url in enumerate(self.urls):
            yield Task(
                request=self.task.request.clone(
                    url=str(url)
                ),
                handler='group',
                group=id(self),
                index=index
            )


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
        self._queue_size = kwargs.get('threads_count', 20) * 2

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

    def add_group(self, group=None, **kwargs):
        '''
        Добавление группы задач
        '''
        if not group:
            group = TasksGroup(**kwargs)

        for task in group.produce_tasks():
            self.add_task(task)

    def size(self):
        '''Размер очереди задач'''
        return self._queue.qsize()

    def get_task(self):
        '''Извлекает задачу'''
        return self._queue.get()

    def empty(self):
        '''Проверяет пустоту очереди'''
        return self._queue.empty()

    def full(self):
        '''Проверяет превышение *рекомендуемого* размера очереди'''
        return self._queue.qsize() == self._queue_size
