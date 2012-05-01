# -*- coding: utf-8 -*-

from random import shuffle
from unittest import TestCase, main

from multifetch import MultiFetcher
from utils.webserver import WebServer

#from tasks.queues import TasksQueue
#from tasks import Task


class Test(TestCase):
    options = dict(
        port=8080,
        response=dict(
            get='Simple GET-response'
        )
    )

    def setUp(self):
        self.server = WebServer(**self.options)
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_multifetcher(self):
        '''Проверка работы MultiFetcher'''

        COUNT = 10

        class Worker(MultiFetcher):
            def __init__(self, *arg, **kwargs):
                super(Worker, self).__init__(*arg, **kwargs)
                self.order = []

            def task_foo(self, task):
                #print task.response.body
                self.order.append(task.index)
                #order.append(task)

        worker = Worker(
            threads_count=COUNT,
            sdfsdf=1,
            sdfsdfww=23
        )

        tasks = range(COUNT)
        shuffle(tasks)

        for task in tasks:
            worker.tasks.add_task(
                index=task,
                priority=task,
                url=self.server.url,
                handler='foo'
            )

        worker.start()

        self.assertListEqual(range(10), worker.order)


if __name__ == "__main__":
    main()
