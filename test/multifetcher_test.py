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

    def test_queue(self):
        '''Проверка работы очереди'''

        COUNT = 10

        class Worker(MultiFetcher):
            def task_foo(self, task):
                print task.response.body
                #order.append(task)

        worker = Worker()

        tasks = range(COUNT)
        shuffle(tasks)

        for task in tasks:
            worker.tasks.add_task(
                index=task,
                url=self.server.url,
                handler='foo'
            )

        worker.start()


if __name__ == "__main__":
    main()
