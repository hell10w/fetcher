# -*- coding: utf-8 -*-

import gevent
from gevent.monkey import patch_all
from gevent.pool import Pool

from empty_dispatch import BaseDispatcher
from fetcher import Fetcher


patch_all(thread=False)


class GreenletDispatcher(BaseDispatcher):
    def __init__(self, **kwargs):
        super(GreenletDispatcher, self).__init__()
        self._pool = Pool(kwargs.pop('threads_count', 10))
        self._finished_tasks = []

    def process_task(self, task):
        def worker(fetcher, task):
            fetcher.prepare_from_task(task)
            fetcher.request()
            fetcher.process_to_task(task)
            return task

        def worker_finished(task):
            self._finished_tasks.append(task)

        self._pool.apply_async(
            worker,
            args=(Fetcher(), task),
            callback=worker_finished
        )

    def is_empty(self):
        return not len(self._pool)

    def is_full(self):
        return self._pool.full()

    def wait_available(self):
        while True:
            gevent.sleep()
            self._pool.wait_available()
            if len(self._finished_tasks) or self.is_empty():
                break

    def finished_tasks(self):
        while self._finished_tasks:
            yield self._finished_tasks.pop()
