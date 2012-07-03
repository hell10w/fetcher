# -*- coding: utf-8 -*-

from cPickle import dumps, loads
from unittest import TestCase, main

from fetcher import FILE_RESPONSE_BODY, MEMORY_RESPONSE_BODY, Task
from fetcher.utils.syncstyle import make

from tests.utils import WebServer, ServerOptions


class Test(TestCase):
    def setUp(self):
        WebServer().start()

    def some_method(self):
        pass

    @classmethod
    def some_class_method(cls):
        pass

    @staticmethod
    def some_static_method():
        pass

    def test_1(self):
        '''Проверка возможности пиклить обработчики задач'''

        task = Task(
            url=ServerOptions.SERVER_URL,
            handler=self.some_method
        )
        task = dumps(task)
        task = loads(task)

        task = Task(
            url=ServerOptions.SERVER_URL,
            handler=self.some_class_method
        )
        task = dumps(task)
        task = loads(task)

        task = Task(
            url=ServerOptions.SERVER_URL,
            handler=self.some_static_method
        )
        task = dumps(task)
        task = loads(task)


if __name__ == "__main__":
    main()
