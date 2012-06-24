# -*- coding: utf-8 -*-

import re
from logging import getLogger, basicConfig, DEBUG

from fetcher import MultiFetcher, Task, Structure as x


logger = getLogger('moviefinder')


class MovieFinder(MultiFetcher):
    def on_start(self):
        logger.debug(u'Добавление инициирующей задачи')
        yield Task(
            url='http://mix.sibnet.ru/movie/',
            handler='prepare'
        )

    def task_prepare(self, task, error=None):
        if task.response.status_code != 200 or error:
            logger.debug(u'Ошибка при выполнении инициирующей задачи!')
            yield task
            return

        count = re.search(
            '\d+',
            task.html.xpath('//div[@class="pager"]/a[last()]/@href')
        )
        count = int(count.group(0))

        logger.debug(u'На сайте %d страниц со списками фильмов' % count)

        self.restart_tasks_generator(
            generator=self.pages_tasks_generator(20)
        )
        #generator=self.pages_tasks_generator(count)

    def pages_tasks_generator(self, count):
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

        items = task.html.structured_xpath(
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

        for item in items:
            print '*' * 80
            for key, value in item.iteritems():
                print '%-11s: %s' % (key, value)
            print


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    worker = MovieFinder(threads_count=3)
    worker.start()
    worker.render_stat()
