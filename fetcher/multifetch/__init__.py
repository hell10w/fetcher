# -*- coding: utf-8 -*-

from sys import modules
from logging import getLogger

from fetcher.cache import CacheExtension
from fetcher.tasks import Task, TasksGroup, Tasks, DataItem, ProcessItem
from fetcher.multifetch.dispatcher import Dispatcher
from fetcher.multifetch.errors import TimeoutError, ConnectionError, AuthError, NetworkError
from fetcher.multifetch.statistics import SpiderStatistics
from fetcher.multifetch.base import SpiderBase


logger = getLogger('fetcher.multifetcher')


# TODO: переделан механизм статистики, но она нигде не обновляется


class MultiFetcher(SpiderBase):
    '''Менеджер асинхроной работы'''

    name = None

    def __init__(self, **kwargs):
        self.statistics = SpiderStatistics()

        self.dispatcher = Dispatcher(**kwargs)
        self.tasks = Tasks(**kwargs)
        self.cache_extension = CacheExtension(**kwargs)

        self.restart_tasks_generator(generator=self.tasks_generator())

    def start(self):
        '''Стартует работу менеджера'''

        self.statistics.reset()

        self._process_for_items(self.on_start())

        try:
            self._should_stop = False

            self._process_for_items(self._process_tasks_generator, limit=True)

            while not self._should_stop:
                while not self.dispatcher.is_full() and not self.tasks.empty():
                    _, task = self.tasks.get_task()
                    if task:
                        if self.cache_process(task):
                            continue
                        self.dispatcher.process_task(task)

                if self.dispatcher.is_empty():
                    break

                self.dispatcher.wait_available()

                for finished_task, error in self.dispatcher.finished_tasks():
                    self.cache_store(finished_task, error)
                    self._process_finished_task(finished_task, error)

                self._process_for_items(self._process_tasks_generator, limit=True)

                self.on_loop()

        except KeyboardInterrupt:
            pass

        self.statistics.hold()

        self.on_stop()

    def stop(self):
        '''Останавливает работу менеджера'''
        self._should_stop = True

    def cache_process(self, task):
        '''Возвращает True если task обработан расширением кэша'''
        if self.cache_extension.is_process_tasks and not task.no_cache_restore:
            without_process, task, error = self.cache_extension.process_task(task)
            if without_process and self.cache_extension.is_good_for_restore(task, error):
                self._process_finished_task(task, error)
                self._process_for_items(self._process_tasks_generator, limit=True)
                return True

    def cache_store(self, task, error=None):
        '''Сохраняет task в кэш если это допустимо'''
        if self.cache_extension.is_process_tasks and not task.no_cache_store:
            if self.cache_extension.is_good_for_store(task, error):
                self.cache_extension.store_task(task, error)

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
        self._process_for_items(self._process_tasks_generator, limit=True)

    def _process_finished_task(self, task, error=None):
        '''Передача управление обработчику для каждого завершенного task'''
        if not task:
            return

        kwargs = dict(
            task=task,
            error=error
        )

        self._process_item(
            ProcessItem(
                handler=getattr(task, 'handler', self.tasks_collector),
                **kwargs
            )
        )

    def _process_for_items(self, generator, limit=None):
        '''Извлекает и добавляет в очередь задания из функции'''
        if not generator:
            return

        if limit:
            if self.tasks.full():
                return

        for item in generator() if callable(generator) else generator:
            if isinstance(item, Task):
                self.tasks.add_task(item)

            elif isinstance(item, DataItem):
                self._process_item(item, prefix='data')

            elif isinstance(item, ProcessItem):
                self._process_item(item)

            elif isinstance(item, TasksGroup):
                item.spider = self
                self.tasks.add_group(item)

            if limit:
                if self.tasks.full():
                    return

    def _process_item(self, process_item, prefix='task'):
        handler = process_item.handler

        if isinstance(handler, str):
            handler = getattr(self, '%s_%s' % (prefix, handler), None)

        elif isinstance(handler, (tuple, list)):
            module, cls, attr = handler
            if module:
                module = getattr(modules[module], cls, None)
            else:
                module = globals()[cls]
            handler = getattr(module, attr, None)

        if callable(handler):
            try:
                self._process_for_items(handler(**process_item.kwargs))
            except Exception:
                self._traceback_logger()
