# -*- coding: utf-8 -*-

import re
from urllib import quote
from logging import getLogger, basicConfig, DEBUG

from fetcher import MultiFetcher, Task, Structure as x, Request, FILE_RESPONSE_BODY, FileCacheBackend
from fetcher.frontend.sqlalchemy_frontend import Model, create_session
from sqlalchemy import Column, Integer, String, Unicode, UnicodeText
from sqlalchemy.orm import relationship


'''class Year(Model):
    __tablename__ = 'years'

    id = Column(Integer, primary_key=True)

    url = Column(String(256))
    name = Column(Integer)


class Kind(Model):
    __tablename__ = 'kinds'

    id = Column(Integer, primary_key=True)

    url = Column(String(256))
    name = Column(Unicode(24))


class Tag(Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)

    url = Column(String(256))
    name = Column(Unicode(24))


class Movie(Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)

    url = Column(String(256))

    title = Column(UnicodeText)
    description = Column(UnicodeText)

    image = Column(String(256))

    year_id = Column(Integer, ForeignKey('year.id'))
    year = relationship('Year')

    kind_id = Column(Integer, ForeignKey('kind.id'))
    kind = relationship('Kind')

    tags = relationship('Tag') #, lazy="dynamic")'''


logger = getLogger('fetcher.moviefinder')


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

        index = re.search(
            '\d+',
            task.html.xpath('//div[@class="pager"]/a[last()]/@href')
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

        #
        # И Л И
        #

        '''
        items = task.html.structured_xpath(
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

        for item in items:
            for key, value in item.iteritems():
                print '%-11s: %s' % (key, value)
            print


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    '''_, session = create_session('sqlite:///:memory:')

    groups = [
        [
            Year,
            [2000, 1967, 1953, 2012],
            lambda year: 'http://example.com/years/%d' % year
        ],
        [
            Tag,
            [u'комедия', u'боевик', u'трэш', u'драма'],
            lambda tag: 'http://example.com/tags/%s' % quote(tag.encode('utf-8'))
        ],
        [
            Kind,
            [u'фильм', u'сериал', u'аниме'],
            lambda tag: 'http://example.com/kinds/%s' % quote(tag.encode('utf-8'))
        ]
    ]


    logger.info(u'Добавление объектов...')
    for model, items, name_2_url in groups:
        for item in items:
            session.add(
                model(
                    url=name_2_url(item),
                    name=item
                )
            )
    session.commit()

    logger.info(u'Подсчет количества объектов...')
    for model, in groups:
        print session.query(model).count()'''



    #Request.body_destination = FILE_RESPONSE_BODY

    if True:
        worker = MovieFinder(threads_count=3)
        worker.start()
        worker.render_stat()
