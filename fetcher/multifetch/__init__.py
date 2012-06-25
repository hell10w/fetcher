# -*- coding: utf-8 -*-

from sys import exc_info
from traceback import extract_tb
from time import time
from logging import getLogger

from fetcher.cache import CacheExtension
from fetcher.tasks import Task, TaskResult, TasksGroup, Tasks
from fetcher.multifetch.dispatcher import Dispatcher
from fetcher.multifetch.errors import TimeoutError, ConnectionError, AuthError, NetworkError


logger = getLogger('fetcher.multifetcher')


class MultiFetcher(object):
    '''Менеджер асинхроной работы'''

    # имя паука - для отображения в админке. по-умолчанию - имя класса
    name = None
    # статистика
    _start_time = 0
    processed_tasks = 0
    processed_from_cache = 0
    transfer_size = 0
    transfer_time = 0

    def __init__(self, **kwargs):
        self.dispatcher = Dispatcher(**kwargs)
        self.tasks = Tasks(**kwargs)
        self.cache_extension = CacheExtension(**kwargs)

        self.restart_tasks_generator(generator=self.tasks_generator())

    def start(self):
        '''Стартует работу менеджера'''

        self._start_time = time()

        self._process_for_tasks(self.on_start())

        try:
            self.processed_tasks = 0
            self.processed_from_cache = 0
            self.transfer_size = 0
            self.transfer_time = 0

            self._should_stop = False

            self._process_for_tasks(self._process_tasks_generator, limit=True)

            while not self._should_stop:
                while not self.dispatcher.is_full() and not self.tasks.empty():
                    _, task = self.tasks.get_task()
                    if task:
                        if self.cache_extension.is_process_tasks:
                            without_process, task, error = self.cache_extension.process_task(task)
                            if without_process and self.is_good_for_restore(task, error):
                                self.processed_from_cache += 1
                                self._process_finished_task(task, error)
                                self._process_for_tasks(self._process_tasks_generator, limit=True)
                                continue
                        self.dispatcher.process_task(task)

                if self.dispatcher.is_empty():
                    break

                self.dispatcher.wait_available()

                for finished_task, error in self.dispatcher.finished_tasks():
                    if self.cache_extension.is_process_tasks:
                        if self.is_good_for_store(finished_task, error):
                            self.cache_extension.store_task(finished_task, error)
                    self._process_finished_task(finished_task, error)

                self._process_for_tasks(self._process_tasks_generator, limit=True)

                self.on_loop()

        except KeyboardInterrupt:
            pass

        self.on_stop()

    def render_stat(self):
        print u'Общее время работы: %.2f секунд' % (time() - self._start_time)
        print u'Обработано задач: %d (из кэша: %d)' % (self.processed_tasks, self.processed_from_cache)
        print u'Суммарное время загрузки каждой задачи: %d секунд' % self.transfer_time
        print u'Суммарный объем загруженных данных: %d байт' % self.transfer_size

    def is_good_for_restore(self, task, error=None):
        '''Годен ли таск для подмены из кэша'''
        return not error and task.response and task.response.url and task.response.status_code == 200

    def is_good_for_store(self, task, error=None):
        '''Годен ли таск для сохранения в кэш'''
        return not error and task.response and task.response.url and task.response.status_code == 200

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
        self._process_for_tasks(self._process_tasks_generator, limit=True)

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

        self.processed_tasks += 1
        self.transfer_size += task.response.size or 0
        self.transfer_time += task.response.total_time or 0

        args = [task]
        if error:
            args.append(error)

        handler = getattr(task, 'handler', self.tasks_collector)

        if type(handler) == str:
            handler = getattr(self, 'task_%s' % handler, None)

        if callable(handler):
            try:
                self._process_for_tasks(handler(*args))
            except Exception, e:
                self._traceback_logger()

    def _process_for_tasks(self, generator, limit=None):
        '''Извлекает и добавляет в очередь задания из функции'''
        if not generator:
            return

        if limit:
            if self.tasks.full():
                return

        for task in generator() if callable(generator) else generator:
            if isinstance(task, Task):
                self.tasks.add_task(task)

            elif isinstance(task, TasksGroup):
                self.tasks.add_group(task)

            if limit:
                if self.tasks.full():
                    return

    def _traceback_logger(self):
        exc_type, exc_value, exc_traceback = exc_info()
        traceback = [
            '  File "%s", line %d, in %s\n    %s' % line
            for line in extract_tb(exc_traceback)
        ]
        logger.error(u'Подавление ошибки в обработчике задачи!')
        logger.error('Traceback:\n' + '\n'.join(traceback))
