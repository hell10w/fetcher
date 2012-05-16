# -*- coding: utf-8 -*-

from fetcher import MultiFetcher


class ProxyFinder(MultiFetcher):
    def on_start(self):
        self.tasks.add_task(
            url='http://google.ru/',
            handler='search'
        )

    def task_search(self, task):
        '''task.setup(
            url='http://www.google.ru/search',
            post=dict(
                q = 'wiki',
                num = 100,
                as_qdr = 'all',
                sclient = '',
                output = ''
            )
        )'''

        #print 'headers: ', task.response.headers
        #print 'body: ', task.response.body

        task.set_input(name='q', value='wiki')
        task.submit()

        self.tasks.add_task(
            task=task,
            handler='result'
        )

    def task_result(self, task):
        '''print '--------------------'
        print '--------------------'
        print 'url: ', task.response.url
        print '--------------------'
        print 'headers: ', task.response.headers
        print '--------------------'
        print 'cookies: ', task.response.cookies
        print '--------------------'
        print 'body: ', task.response.body
        print '--------------------'''
        #print task.html_tree
        #print task.html_tree.forms[0].fields
        #print task.form_fields()
        links = task.xpath_list('//li/h3/a[1]')
        print len(links)
        for link in links:
            print '%s [%s]' % (link.text_content(), link.attrib['href'])


if __name__ == '__main__':
    proxy_finder = ProxyFinder()
    proxy_finder.start()
