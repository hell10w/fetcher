# -*- coding: utf-8 -*-

from unittest import TestCase, main

from fetcher import MultiFetcher, Task, DataItem

from tests.utils import WebServer, ServerOptions


class Test(TestCase):
    def setUp(self):
        WebServer().start()

    def test_1(self):
        '''Общая проверка работы паука и работы приоритетов задач'''

        TASKS_COUNT = 100
        ServerOptions.RESPONSE['GET'] = 'checking get method'

        class Spider(MultiFetcher):
            def tasks_generator(self):
                self.order = []
                for _ in xrange(TASKS_COUNT):
                    yield Task(
                        url=ServerOptions.SERVER_URL,
                        priority=_ + 1
                    )

            def tasks_collector(self, task, error=None):
                self.order.append(task.priority)

        spider = Spider(threads_count=1)
        spider.start()

        self.assertListEqual(spider.order, range(1, TASKS_COUNT + 1))

    def test_2(self):
        '''Проверка разных обработчиков задач'''

        ServerOptions.RESPONSE['GET'] = 'checking handlers'

        class Spider(MultiFetcher):
            def tasks_generator(self):
                self.handlers = dict(
                    named=False,
                    method=False,
                    static=False,
                    dataitem=False
                )

                yield Task(
                    handler='named',
                    url=ServerOptions.SERVER_URL
                )
                yield Task(
                    handler=self.task_method,
                    url=ServerOptions.SERVER_URL
                )
                yield Task(
                    handler=Test.task_static,
                    spider=self,
                    url=ServerOptions.SERVER_URL
                )
                yield DataItem(
                    handler='item',
                    param1='param1',
                    param2=100500
                )

            def task_named(self, task, error=None):
                self.handlers['named'] = True

            def task_method(self, task, error=None):
                self.handlers['method'] = True

            def data_item(self, **kwargs):
                self.handlers['dataitem'] = True

            def tasks_collector(self, task, error=None):
                raise Exception()

        spider = Spider(threads_count=1)
        spider.start()

        self.assertTrue(all(spider.handlers.values()))

    @classmethod
    def task_static(cls, task, error=None):
        task.spider.handlers['static'] = True


if __name__ == "__main__":
    main()
