# -*- coding: utf-8 -*-

from fetcher import MultiFetcher


class ProxyFinder(MultiFetcher):
    def on_start(self):
        self.tasks.add_task(
            url='http://google.ru/',
            handler='search'
        )

    def task_search(self, task, error=None):
        task.set_input(name='q', value='proxy list')
        task.submit()
        yield task.setup(handler='result')

    def task_result(self, task, error=None):
        if error:
            print 'Ошибка при загрузке выдачи гугла. Повтор...'
            yield task
            return
        links = task.xpath_list('//li/h3/a[1]/@href')
        links = map(str, links)
        links = [
            link.split('?q=', 1)[1].split('&sa=', 1)[0]
            for link in links
            if link.startswith('/url')
        ]
        print 'Найдено %d ссылок. Переход...' % (len(links))
        for link in links:
            self.tasks.add_task(
                url=link,
                handler='site'
            )

    def task_site(self, task, error=None):
        print task


if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    proxy_finder.start()
