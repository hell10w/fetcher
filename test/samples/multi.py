# -*- coding: utf-8 -*-

from multifetch import MultiFetcher


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        self.index = 0

        for _ in xrange(1000):
            self.tasks.add_task(
                url='http://localhost',
                index=_
            )

    def tasks_collector(self, task):
        print self.index, task.index
        self.index += 1


worker = Worker(
    threads_count=20,
    queue_transport='memory'
)
worker.start()
