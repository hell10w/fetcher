# -*- coding: utf-8 -*-

from time import time
from logging import getLogger, basicConfig, DEBUG

from lxml.html import tostring
from werkzeug.urls import url_fix
from sqlalchemy.sql.expression import or_, not_, and_

from fetcher import MultiFetcher, CACHE_RESPONSE, Task, Structure as x, Chunk as c
from fetcher.frontend.flask_frontend import Frontend, app, database, model


WORKER_IN_FRONTEND = 0
CONNECTION_STRING = 'sqlite:///mcgrp.db'
#CONNECTION_STRING = 'mysql://root:654321@localhost/mcgrp'


logger = getLogger('fetcher.worker')


class Url(model):
    MAGIC = int(time())
    NEW_URL, LOOKING, MAP_URL, BOOK_URL = range(4)

    id = database.Column(database.Integer, primary_key=True)
    url = database.Column(database.Text) #, unique=True)
    type_ = database.Column(database.Integer)

    magic = database.Column(database.Integer)

    def __init__(self, **kwargs):
        kwargs.setdefault('magic', Url.MAGIC)
        super(Url, self).__init__(**kwargs)


class McgrpRu(MultiFetcher):
    def on_start(self):
        task, record = self.get_url('http://mcgrp.ru')
        if task:
            if record:
                record.type_ = Url.LOOKING
                database.session.commit()
            yield task

    def get_url(self, url, make_task=True, make_record=True):
        task = None
        url = unicode(url.rstrip('/'))
        url = url_fix(url)
        record = Url.query.filter_by(url=url).first()
        if make_record and not record:
            record = Url(
                url=url,
                type_=Url.NEW_URL
            )
            database.session.add(record)
        if make_task:
            task = Task(
                url=unicode(url),
                handler='check'
            )
        return task, record

    def save_state(self, url, state):
        _, record = self.get_url(url, make_task=False, make_record=False)
        if record:
            record.type_ = state
            database.session.commit()
        else:
            logger.error(u'Существует URL отличный от сохраненного - его состояние не будет изменено!')

    def exists_tasks(self):
        return Url.query.filter(
            and_(
                not_(Url.magic==Url.MAGIC),
                not_(Url.type_==Url.LOOKING)
            )
        ).count()

    def urls_processor(self):
        while self.exists_tasks():
            urls = Url.query.filter(
                and_(
                    not_(Url.magic==Url.MAGIC),
                    not_(Url.type_==Url.LOOKING)
                )
            ).limit(20)
            for url in urls:
                url.type_ = url.LOOKING
                url.magic = url.MAGIC
                database.session.commit()
                task, _ = self.get_url(url.url, make_record=False)
                yield task

        logger.info(u'Url для проверки больше нет.')
        yield 0

    def task_check(self, task, error=None):
        if task.response.status_code != 200:
            logger.error(u'Задача %s завершилась с ошибкой - повтор!' % task.request.url)
            yield task
            return

        if task.xpath_exists('//*[@name="subBuy"]'):
            self.prepare_page(task)
        else:
            self.prepare_map(task)

    def prepare_map(self, task):
        task.make_links_absolute()
        urls = set(task.xpath_list('//div[@id="content"]//a[starts-with(@href, "http://mcgrp.ru/")]/@href'))

        logger.info(u'Найдено %d ссылок на странице %s %s' %
            (
                len(urls),
                task.request.url,
                u'(из кэша)' if task.response.is_from_cache else ''
            )
        )

        if urls:
            for url in urls:
                self.get_url(url, make_task=False)
            database.session.commit()

        if not self.tasks_generator_enabled:
            if self.exists_tasks():
                logger.info(u'Перезапуск генератора задач')
                self.restart_tasks_generator(self.urls_processor())

        self.save_state(task.request.url, Url.MAP_URL)

    def prepare_page(self, task):
        item = task.structured_xpath(
            '//div[@id="content"]',
            x(
                './table[4]/tbody/tr',
                class_='./td[1]/text()',
                group='./td[2]/text()',

                ),
            x(
                './/*[@id="fd_3"]',
                name='./h2/text()',
                description='./p/text()'
            ),
            #tables=c(
            #    './/table[@class="descr_table"]',
            #    apply_func=tostring,
            #    one=False
            #),
            brand='./h3[1]/text()',
            filetype='./h3[2]/text()',
            filesize='./b[2]/text()',
            image='./a/img/@src'
        )

        print len(item)
        for p in item:
            #print '-' * 20, len(p.tables)
            for key, value in p.iteritems():
                print '%-11s: %s' % (key, value)

        self.save_state(task.request.url, Url.BOOK_URL)


if __name__ == '__main__':
    frontend = Frontend(McgrpRu, connection_string=CONNECTION_STRING)
    frontend.add_view(Url)

    if not WORKER_IN_FRONTEND:
        basicConfig(level=DEBUG)
        database.create_all()
        worker = McgrpRu(cache_type=CACHE_RESPONSE)
        worker.start()
    else:
        frontend.run()
