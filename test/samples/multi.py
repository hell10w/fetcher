# -*- coding: utf-8 -*-

from time import time

import gevent
import requests

from tasks import Task
from multifetch import MultiFetcher


URLS = [
    'http://google.ru/',
    'http://yandex.ru/',
    #'http://rambler.ru/',
    'http://aport.ru/',
    'http://yahoo.com/'
]


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        #if True:
        #    return

        for url in URLS:
            self.tasks.add_task(
                url=url,
                handler='finded'
            )

    def task_finded(self, task):
        #print task, task.response.status_code,
        #if task.response.body:
        #    print task.url, task.response.body.split('<title>', 1)[1].split('</title>', 1)[0]
        #else:
        #    print
        pass


def timeit(func):
    start = time()
    func()
    print time() - start



def worker_test():
    worker = Worker()
    worker.start()


def direct_test():
    gs = [gevent.spawn(requests.get, url) for url in URLS]
    gevent.joinall(gs)


direct_test()


timeit(worker_test)
timeit(direct_test)