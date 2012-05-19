# -*- coding: utf-8 -*-

from fetcher import MultiFetcher


class ProxyFinder(MultiFetcher):
    def on_start(self):
        self.tasks.add_task(
            url='http://google.ru/',
            handler='search'
        )

    def task_search(self, task):
        print task.js

        #task.set_input(name='q', value='wiki')
        #task.submit()

        return

        self.tasks.add_task(
            task=task,
            handler='result'
        )

    def task_result(self, task):
        links = task.xpath_list('//li/h3/a[1]')
        print len(links)
        for link in links:
            print '%s [%s]' % (link.text_content(), link.attrib['href'])


if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    proxy_finder.start()
