# -*- coding: utf-8 -*-

from time import time

from multifetch import MultiFetcher, MemoryQueue, MongoQueue


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        self.index = 0

        for _ in xrange(1000):
            self.tasks.add_task(
                url='http://localhost',
                index=_ + 1
            )

    def tasks_collector(self, task):
        if task.index % 100 == 0:
            print task.index,


def worker(queue=MemoryQueue, repeat=4):
    elapsed = 0
    for _ in range(repeat):
        start = time()
        worker = Worker(
            threads_count=20,
            queue=queue
        )
        worker.start()
        elapsed += time() - start
    print
    print elapsed / repeat
    print

worker()
worker(queue=MongoQueue)
#worker(processes_count=2)
#worker(processes_count=4)
