# -*- coding: utf-8 -*-

import gevent
from gevent.monkey import patch_all
from gevent.pool import Pool

from empty_dispatch import BaseDispatcher
from fetcher import get_fetcher_transport


patch_all(thread=False)


class GreenletDispatcher(BaseDispatcher):
    '''Менеджер асинхронной работы основанный на gevent'''

    def __init__(self, **kwargs):
        super(GreenletDispatcher, self).__init__()
        self._fetcher_class = get_fetcher_transport(**kwargs)
        self._pool = Pool(kwargs.pop('threads_count', 10))
        self._finished_tasks = []

    def process_task(self, task):
        '''Стартует выполнение задачи'''

        def worker(fetcher, task):
            '''Преобразует задачу в запрос, выполняет его и возвращает'''
            fetcher.prepare_from_task(task)
            fetcher.request()
            fetcher.process_to_task(task)
            return task

        def worker_finished(task):
            '''Добавляет выполненную задачу в список выполненных'''
            self._finished_tasks.append(task)

        self._pool.apply_async(
            worker,
            args=(self._fetcher_class(), task),
            callback=worker_finished
        )

    def is_empty(self):
        '''Проверяет пустоту пула выполняемых задач'''
        return not len(self._pool)

    def is_full(self):
        '''Проверяет заполненность пула выполняемых задач'''
        return self._pool.full()

    def wait_available(self):
        '''Ожидание появления пустых слотов в пуле выполняемых задач'''
        while True:
            gevent.sleep()
            self._pool.wait_available()
            if len(self._finished_tasks) or self.is_empty():
                break

    def finished_tasks(self):
        '''Итерирует список выполненных задач'''
        while self._finished_tasks:
            yield self._finished_tasks.pop()
