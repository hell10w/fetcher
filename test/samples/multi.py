# -*- coding: utf-8 -*-

from multifetch import MultiFetcher


URLS = [
    'http://google.ru/',
    'http://yandex.ru/',
    'http://rambler.ru/',
    'http://aport.ru/',
    'http://yahoo.com/'
]


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        for url in URLS:
            self.tasks.add_task(
                url=url,
                handler='finded'
            )

    def task_finded(self, task):
        print task.response.url
        print '  ', task.response.status_code
        print '  ', task.response.cookies
        print '  ', task.response.headers
        print '  ', task.response.body.name


worker = Worker()
worker.start()
