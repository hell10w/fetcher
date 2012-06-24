# -*- coding: utf-8 -*-

from fetcher import MultiFetcher, Task


class ProxyFinder(MultiFetcher):
    def on_start(self):
        yield Task(
            url='http://google.ru/',
            handler='search'
        )

    def task_search(self, task, error=None):
        if error or task.response.status_code != 200:
            yield task
            return

        task.get_control('q').value = u'кириллица'
        task.submit()
        yield task.setup(handler='result')

    def task_result(self, task, error=None):
        if error:
            print 'Ошибка при загрузке выдачи гугла. Повтор...'
            yield task
            return

        links = task.html.structured_xpath(
            '//li/h3/a[1]',
            href='./@href',
            title=('.', lambda item: item.text_content())
        )

        for link in links:
            print link.href
            print link.title
            print '*' * 80


if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    proxy_finder.start()
