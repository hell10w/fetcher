# -*- coding: utf-8 -*-

from time import time

from fetcher import MultiFetcher, MemoryQueue, MongoQueue, Task


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        self.index = 0

    def tasks_generator(self):
        for _ in xrange(1000):
            yield Task(
                url='http://localhost',
                index=_ + 1
            )

    def tasks_collector(self, task):
        if task.index % 100 == 0:
            print task.index,


def worker(queue=MemoryQueue, repeat=6):
    elapsed = 0
    for _ in range(repeat):
        start = time()
        worker = Worker(
            threads_count=40,
            queue=queue
        )
        worker.start()
        elapsed += time() - start
    print
    print elapsed / repeat
    print


worker()
