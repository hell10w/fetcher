# -*- coding: utf-8 -*-

from time import time

from grab.spider import Spider, Task as GrabTask
from fetcher import MultiFetcher, Task as FetcherTask


TASKS_COUNT = 1500
TESTS_COUNT = 10


def timeit(function, count=None, *args, **kwargs):
    COUNT = count or TESTS_COUNT
    elapsed = 0
    for _ in xrange(COUNT):
        started = time()
        function(*args, **kwargs)
        elapsed += time() - started
    print '%s started %d times, average time: %f' % (str(function), COUNT, elapsed / COUNT)


def worker_spider():
    class Worker(Spider):
        def task_generator(self):
            for _ in xrange(TASKS_COUNT):
                yield GrabTask(
                    url='http://localhost',
                    name='foo'
                )

        def task_foo(self, grab, task):
            pass

    worker = Worker(thread_number=30)
    worker.run()


def worker_fetcher():
    class Fetcher(MultiFetcher):
        def tasks_generator(self):
            for _ in xrange(TASKS_COUNT):
                yield FetcherTask(url='http://localhost', handler='foo')

        def task_foo(self, task, error=None):
            pass

    fetcher = Fetcher(threads_count=30)
    fetcher.start()


timeit(worker_spider)
timeit(worker_fetcher)
