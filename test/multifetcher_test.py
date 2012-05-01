# -*- coding: utf-8 -*-

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

    @classmethod
    def setUpClass(cls):
        '''Запускает сервер'''
        cls.server = WebServer(**cls.options)
        cls.server.start()

    @classmethod
    def setDownClass(cls):
        '''Вырубает сервер'''
        cls.server.stop()

    def test_queue(self):
        '''Проверка работы очереди'''

        order = []

        class Worker(MultiFetcher):
            def task_temp(self, task):
                print task.response.body
                order.append(task)

        worker = Worker()
        for index in range(10):
            worker.tasks.add_task(
                url=self.server.url,
                index=index,
                handler=Worker.task_temp
            )
        worker.start()

        print order

        #self.assertListEqual(numbers, range(count))


if __name__ == "__main__":
    main()
