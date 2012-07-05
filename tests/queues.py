# -*- coding: utf-8 -*-

from time import time
from unittest import TestCase, main

from fetcher import Task
from fetcher.tasks.queues.sqla import Queue

from tests.utils import WebServer, ServerOptions


class Test(TestCase):
    def test_1(self):
        '''Проверка работы очереди с таймаутами'''

        queue = Queue('sqlite://')

        for _ in xrange(100):
            queue.put((_, _))

        extracted = [queue.get()[1] for _ in xrange(100)]

        self.assertListEqual(extracted, range(100))

    def test_2(self):
        queue = Queue('sqlite://')

        timeout = 2.0

        start_time = time()

        queue.put(
            (
                0,
                Task(
                    timeon=timeout,
                    text='Hello world!'
                )
            )
        )
        queue.get()

        self.assertGreaterEqual(time(), start_time + timeout)


if __name__ == "__main__":
    main()
