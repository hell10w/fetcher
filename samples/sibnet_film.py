# -*- coding: utf-8 -*-

import re
from logging import getLogger, basicConfig, DEBUG

from fetcher import MultiFetcher, Task, Structure as x, Response, FileCacheBackend
#from fetcher.frontend import FlaskFrontend, database, model


logger = getLogger('fetcher.moviefinder')


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
        logger.debug(u'Добавление инициирующей задачи')
        yield Task(
            url='http://mix.sibnet.ru/movie/',
            handler='prepare'
        )

    def task_prepare(self, task, error=None):
        if task.response.status_code != 200:
            yield task
            return

        index = re.search(
            '\d+',
            task.xpath('//div[@class="pager"]/a[last()]/@href')
        )
        index = int(index.group(0))

        logger.debug(u'На сайте №%d страниц со списками фильмов' % index)

        self.restart_tasks_generator(
            generator=self.pages_tasks_generator(20)
        )
        #generator=self.pages_tasks_generator(index)

    def pages_tasks_generator(self, count):
        #for index in xrange(1, 2):
        for index in xrange(1, count + 1):
            logger.debug(u'Добавление в задачи страницы №%d со списком фильмов' % index)
            yield Task(
                url='http://mix.sibnet.ru/movie/page,%d/' % index,
                handler='page'
            )

    def task_page(self, task, error=None):
        if task.response.status_code != 200:
            logger.debug(u'Код возврата неверный (!=200) - повтор задачи')
            yield task
            return

        logger.debug(u'Задача выполнена %s успешно' % task.request.url)

        items = task.structured_xpath(
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

        logger.debug(u'Извлечено %d фильмов' % len(items))

        #
        # И Л И
        #

        '''
        items = task.structured_xpath(
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
        '''

        '''for item in items:
            for key, value in item.iteritems():
                print '%-11s: %s' % (
                    MovieFinder.ROWS[key],
                    value
                )
            print'''


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    worker = MovieFinder(
        threads_count=3,
        cache_backend=FileCacheBackend,
        cache_path='/tmp/cachee/'
    )
    worker.start()
    worker.render_stat()
