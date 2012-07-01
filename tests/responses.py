# -*- coding: utf-8 -*-

from cPickle import dumps, loads
from unittest import TestCase, main

from fetcher import FILE_RESPONSE_BODY, MEMORY_RESPONSE_BODY, Task
from fetcher.utils.syncstyle import make

from tests.utils import WebServer, ServerOptions


class Test(TestCase):
    def setUp(self):
        WebServer().start()

    def test_1(self):
        '''Проверка правильности работы с разными способами сохранения ответов сервера'''

        DATA = 'checking get method'
        ServerOptions.RESPONSE['GET'] = DATA

        task, error = make(
            Task(
                url=ServerOptions.SERVER_URL,
                body_destination=FILE_RESPONSE_BODY
            )
        )
        self.assertIsNotNone(task.response.body)
        self.assertTrue(task.response.body.validate())
        self.assertEqual(task.response.content, DATA)

        task = dumps(task)
        task = loads(task)

        self.assertIsNotNone(task.response.body)
        self.assertTrue(task.response.body.validate())
        self.assertEqual(task.response.content, DATA)

        task, error = make(
            Task(
                url=ServerOptions.SERVER_URL,
                body_destination=MEMORY_RESPONSE_BODY
            )
        )
        self.assertIsNotNone(task.response.body)
        self.assertTrue(task.response.body.validate())
        self.assertEqual(task.response.content, DATA)

        task = dumps(task)
        task = loads(task)

        self.assertIsNotNone(task.response.body)
        self.assertTrue(task.response.body.validate())
        self.assertEqual(task.response.content, DATA)


if __name__ == "__main__":
    main()
