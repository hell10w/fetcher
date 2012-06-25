import cProfile

from fetcher import MultiFetcher, Task


def worker_fetcher():
    class Fetcher(MultiFetcher):
        def tasks_generator(self):
            for _ in xrange(10000):
                yield Task(url='http://localhost', handler='foo')

        def task_foo(self, task, error=None):
            pass

    fecher = Fetcher(threads_count=30)
    fecher.start()


cProfile.run('worker_fetcher()', sort=1)
