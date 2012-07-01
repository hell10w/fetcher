# -*- coding: utf-8 -*-

from logging import getLogger

from fetcher.fetch import Extensions, Response, Request
from fetcher.utils import import_module


logger = getLogger('fetcher.tasks')


class Task(Extensions):
    '''Отдельная задача'''

    debug = False

    def __init__(self, **kwarg):
        self.no_cache_store = False
        self.no_cache_restore = False

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
            if not key[0] == '_'
        )
        return Task(**_kwargs).setup(**kwargs)

    def process_response(self):
        '''Подготовка будущего запроса исходя из ответа'''
        self.request.url = self.response.url
        self.request.cookies.update(self.response.cookies)
        self.request.post = None
        self.request.method = 'GET'
        self.request.is_multipart_post = False


class ProcessItem(object):
    def __init__(self, handler, **kwargs):
        self.handler = handler
        self.kwargs = kwargs


class DataItem(ProcessItem):
    '''Элемент данных для отсылки обработчику'''


class TasksGroup(object):
    '''Группа задач'''

    groups = {}

    class DotDict(dict):
        def __getattr__(self, name):
            return self[name]

        def __setattr__(self, key, value):
            self[key] = value

    def __init__(self, base_task, load_urls, spider=None, **kwarg):
        TasksGroup.groups[id(self)] = self

        self.spider = spider
        self.task = base_task
        self.load_urls = load_urls

        self.__count = len(load_urls)
        self.tasks = [TasksGroup.DotDict() for _ in range(self.__count)]

        self.setup(**kwarg)

    def __del__(self):
        TasksGroup.groups.pop(id(self), None)

    def setup(self, **kwarg):
        '''Настройка параметров'''
        for name, value in kwarg.iteritems():
            setattr(self, name, value)

    def produce_tasks(self):
        '''Генератор задач '''
        for index, url in enumerate(self.load_urls):
            yield Task(
                request=self.task.clone(
                    url=str(url)
                ),
                handler=(__name__, 'TasksGroup', '_task_item'),
                priority=1,
                internal_data=TasksGroup.DotDict(
                    group=id(self),
                    index=index
                )
            )

    @classmethod
    def _task_item(cls, task, error=None):
        '''Внутренний обработчик загрузки зачади из группы'''
        internal_data = task.internal_data

        group = TasksGroup.groups.get(internal_data.group, None)

        item = group.tasks[internal_data.index]
        item.task = task
        item.error = error

        group.__count -= 1

        if not group.__count:
            default_handler = group.spider.groups_collector
            if not default_handler:
                default_handler = (__name__, 'TasksGroup', 'groups_collector')

            yield ProcessItem(
                handler=getattr(group, 'handler', default_handler),
                group=group
            )


class Tasks(object):
    '''Менеджер задач'''

    def __init__(self, queue='memory', threads_count=20, **kwargs):
        '''
        Конструктор менеджера задач.
        Параметры:
            tasks_container - тип контейнера для хранения задач.
                Может принимать следующие значения: memory, mongo
        '''

        #self._queue = queue(**kwargs)

        if isinstance(queue, str):
            try:
                queue = import_module('fetcher.tasks.queues.%s' % queue).Queue
            except ImportError:
                raise Exception(u'Неудалось импортировать класс реализации очереди задач! Проверьте аргументы!')
        if queue:
            logger.info(u'Использование в качестве очереди задач %s' % queue)
            self._queue = queue(**kwargs)

        self._queue_size = threads_count * 2


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
            task.setup(**kwargs)

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
        return self._queue.size()

    def get_task(self):
        '''Извлекает задачу'''
        return self._queue.get()

    def empty(self):
        '''Проверяет пустоту очереди'''
        return not self._queue.size()

    def full(self):
        '''Проверяет превышение *рекомендуемого* размера очереди'''
        return self._queue.size() == self._queue_size
