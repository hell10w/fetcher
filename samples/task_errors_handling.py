# -*- coding: utf-8 -*-

from logging import DEBUG, basicConfig

from fetcher import MultiFetcher, Task


class SimpleSpider(MultiFetcher):
    def on_start(self):
        yield Task(
            url='http://google.ru/',
            handler='handler1'
        )
        yield Task(
            url='http://google.ru/',
            handler='handler2'
        )

    def task_handler1(self, task, error=None):
        raise IndexError(u'какая-то ошибка')

    def task_handler2(self, task, error=None):
        raise ZeroDivisionError('Big problem!')


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    worker = SimpleSpider()
    worker.start()
