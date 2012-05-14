# -*- coding: utf-8 -*-

from fetcher import MultiFetcher


class ProxyFinder(MultiFetcher):
    def on_start(self):
        self.tasks.add_task(
            url='http://google.ru/',
            handler='search'
        )

    def task_search(self, task):
        task.setup(
            url='http://www.google.ru/search',
            post=dict(
                q = 'wiki',
                num = 10,
                as_qdr = 'all',
                sclient = '',
                output = ''
            )
        )
        self.tasks.add_task(
            task=task,
            handler='result'
        )

    def task_result(self, task):
        print '--------------------'
        print '--------------------'
        print 'url: ', task.response.url
        print '--------------------'
        print 'headers: ', task.response.headers
        print '--------------------'
        print 'cookies: ', task.response.cookies
        print '--------------------'
        print 'body: ', task.response.body
        print '--------------------'
        print task.html_tree
        print task.xpath_list('//a/@href')


if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    proxy_finder.start()
