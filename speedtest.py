from random import choice
from string import ascii_letters
from time import time

import requests
import gevent
from gevent.monkey import patch_all

from grab.spider import Spider, Task

from fetcher.multifetch import MultiFetcher

patch_all(thread=False)


TESTS_COUNT = 5
URLS_COUNT = 10


def generate_string():
    return ''.join([choice(ascii_letters) for _ in range(20)])


URLS = ['http://google.ru/'+generate_string() for _ in range(URLS_COUNT)]


def timeit(function, count=None, *args, **kwargs):
    COUNT = count or TESTS_COUNT
    elapsed = 0
    for _ in xrange(COUNT):
        started = time()
        gevent.spawn(function, *args, **kwargs).join()
        elapsed += time() - started
    print '%s started %d times, average time: %f' % (str(function), COUNT, elapsed / COUNT)


def test_grab():
    class TestSpider(Spider):
        initial_urls = URLS

        def task_initial(self, grab, task):
            pass

    spider = TestSpider(
        thread_number=10
    )
    spider.run()


def test_gevent():
    def worker(url):
        response = requests.get(url)

    r = [gevent.spawn(worker, url) for url in URLS]
    gevent.joinall(r)


def test_multifetcher():
    class Fetcher(MultiFetcher):
        def __init__(self, *args, **kwargs):
            super(Fetcher, self).__init__(*args, **kwargs)
            for url in URLS:
                self.tasks.add_task(
                    url=url,
                    handler='finished'
                )

        def task_finished(self, task):
            pass

    fetcher = Fetcher(
        queue_transport='memory'
    )
    fetcher.start()


if False:
    timeit(test_gevent)
    timeit(test_multifetcher)
    timeit(test_grab)


def worker_spider():
    class Worker(Spider):
        def task_generator(self):
            for _ in xrange(1500):
                yield Task(url='http://localhost')

        def task_initial(self, grab, task):
            pass

    worker = Worker(
        thread_number=30
    )
    worker.run()


def worker_fetcher():
    class Fetcher(MultiFetcher):
        def __init__(self, **kwargs):
            kwargs.setdefault('queue_transport', 'memory')
            kwargs.setdefault('threads_count', 30)

            super(Fetcher, self).__init__(**kwargs)

            for _ in xrange(1500):
                self.tasks.add_task(url='http://localhost')

    fecher = Fetcher()
    fecher.start()


timeit(worker_fetcher)
timeit(worker_spider)

#import cProfile
#cProfile.run('worker_spider()')
#cProfile.run('worker_fetcher()')


