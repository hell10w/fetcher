# -*- coding: utf-8 -*-

import re

from fetcher import MultiFetcher, Task
from fetcher.fetch.extensions.lxml_ext import Structure as x


class MovieFinder(MultiFetcher):
    ROWS = dict(
        kind=u'тип',
        year=u'год',
        description=u'описание',
        url=u'URL',
        title=u'название',
        img=u'превью',
        tags=u'теги'
    )

    def on_start(self):
        yield Task(
            url='http://mix.sibnet.ru/movie/',
            handler='prepare'
        )

    def task_prepare(self, task, error=None):
        if task.response.code != 200:
            yield task
            return

        index = re.search(
            '\d+',
            task.xpath('//div[@class="pager"]/a[last()]/@href')
        )
        index = int(index.group(0))

        self.restart_tasks_generator(
            generator=self.pages_tasks_generator(index)
        )

    def pages_tasks_generator(self, count):
        #for index in xrange(1, count + 1):
        for index in xrange(1, 2):
            yield Task(
                url='http://mix.sibnet.ru/movie/page,%d/' % index,
                handler='page'
            )

    def task_page(self, task, error=None):
        if task.response.code != 200:
            yield task
            return

        items = task.crazy_grab(
            x(
                '//div[@class="b-mini-card"]/div/div',
                x(
                    './div[1]',
                    kind='./a[1]/text()',
                    year='./a[2]/text()',
                ),
                x(
                    './div[@class="b-mini-card__body"]',
                    x(
                        './h2/a',
                        url='./@href',
                        title='./text()'
                    ),
                    description='./div[@class="b-mini-card__desc"]/text()',
                    tags=x(
                        './div[@class="b-mini-card__tags"]/a',
                        url='./@href',
                        name='./text()'
                    )
                ),
                img='./a[1]/img/@src'
            )
        )

        for item in items:
            for key, value in item.iteritems():
                print '%-11s: %s' % (
                    MovieFinder.ROWS[key],
                    value
                )
            print


if __name__ == '__main__':
    spider = MovieFinder(
        threads_count=3
    )
    spider.start()
