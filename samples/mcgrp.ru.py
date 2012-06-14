# -*- coding: utf-8 -*-

from logging import getLogger, basicConfig, DEBUG

from lxml.html import tostring
from werkzeug.urls import url_fix
from sqlalchemy.sql.expression import or_, not_, and_

from fetcher import MultiFetcher, MongoCacheBackend, MySQLCacheBackend, \
                    CACHE_RESPONSE, Task, \
                    Structure as x, Chunk as c, Request, MEMORY_RESPONSE_BODY
from fetcher.frontend.flask_frontend import Frontend, app, database, model


Request.body_destination = MEMORY_RESPONSE_BODY


WORKER_IN_FRONTEND = 0
#CONNECTION_STRING = 'sqlite:///mcgrp.db'
CONNECTION_STRING = 'mysql://root:654321@localhost/mcgrp'


logger = getLogger('fetcher.worker')


class Url(model):
    NEW_URL, LOOKING, MAP_URL, PAGE_URL = range(4)

    id = database.Column(database.Integer, primary_key=True)

    url = database.Column(database.Text) #, unique=True)

    level = database.Column(database.Integer)
    type_ = database.Column(database.Integer)

    def __init__(self, **kwargs):
        kwargs.setdefault('type_', Url.NEW_URL)
        super(Url, self).__init__(**kwargs)


class Page(model):
    id = database.Column(database.Integer, primary_key=True)

    url = database.Column(database.Text)

    code = database.Column(database.String(16))

    class_ = database.Column(database.Text)
    group = database.Column(database.Text)
    name = database.Column(database.Text)

    type_ = database.Column(database.String(16))
    size_ = database.Column(database.String(16))

    image_url = database.Column(database.Text)
    image = database.Column(database.BLOB)

    description = database.Column(database.Text)


PREPARE_MAP, PREPARE_MAP_ERRORS, PREPARE_PAGE, PREPARE_IMAGE = range(4)


class McgrpRu(MultiFetcher):
    work_type = PREPARE_MAP

    def on_start(self):
        if self.work_type == PREPARE_MAP:
            logger.info(u'Создание инициальной задачи')
            self.store_url('http://mcgrp.ru', commit=True)

        self.restart_tasks_generator(self.tasks_generator())

    def clear_urls(self):
        logger.info(u'Очистка таблицы. Старых записей - %d' % Url.query.count())
        for urls in Url.query.yield_per(100):
            database.session.delete(urls)
        database.session.commit()

    def save_state(self, url, state, commit=True):
        record = Url.query.filter_by(url=self.fix_url(url)).first()
        if not record:
            logger.error(u'Не найден Url для сохранения состяния проверенности - %s!' % task.request.url)
            return
        record.type_ = state
        if commit:
            database.session.commit()

    def fix_url(self, url):
        return url_fix(unicode(url.rstrip('/')))

    def store_url(self, url, level=0, commit=False):
        url = self.fix_url(url)
        record = Url.query.filter_by(url=url).first()
        if record:
            return
        else:
            record = Url(
                url=url,
                level=level
            )
            database.session.add(record)

        if commit:
            database.session.commit()

    def tasks_generator(self):
        if self.work_type == PREPARE_MAP:
            while True:
                urls = Url.query.filter(and_(Url.type_ == Url.NEW_URL, Url.level < 2)).limit(20).all()
                if not urls:
                    break

                for url in urls:
                    task = Task(
                        url=url.url,
                        level=url.level,
                        handler='map'
                    )
                    url.type_ = Url.LOOKING
                    yield task

                database.session.commit()

        elif self.work_type == PREPARE_MAP_ERRORS:
            urls = Url.query.filter(and_(Url.type_ == Url.LOOKING, Url.level < 2)).all()
            logger.info(u'В базе %d отработавших с ошибкой Url.' % len(urls))
            for url in urls:
                task = Task(
                    url=url.url,
                    level=url.level,
                    handler='map'
                )
                yield task

        elif self.work_type == PREPARE_PAGE:
            urls = Url.query.filter_by(type_=Url.LOOKING, level=2).all()
            if urls:
                logger.error(u'Незаконченных задач с прошлой сессии: %d' % len(urls))
            else:
                urls = Url.query.filter_by(type_=Url.NEW_URL, level=2).limit(20).all()

            while urls:
                if not urls:
                    break

                for url in urls:
                    task = Task(
                        url=url.url,
                        handler='page'
                    )
                    url.type_ = Url.LOOKING
                    yield task

                database.session.commit()

                urls = Url.query.filter_by(type_=Url.NEW_URL, level=2).limit(20).all()

        elif self.work_type == PREPARE_IMAGE:
            pass

        logger.info(u'Url для проверки больше нет.')
        yield 0

    def task_map(self, task, error=None):
        if error:
            logger.error(u'Ошибка при загрузке %s. Повтор.' % task.request.url)
            yield task
            return

        if task.level > 1:
            logger.error(u'Уровень вложенности > 2 на %s' % task.response.url)
            return

        try:
            task.make_links_absolute()
        except:
            print task.response, task.response.url
            return

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
                self.store_url(url, level=task.level + 1)
            database.session.commit()

        if not self.tasks_generator_enabled:
            if Url.query.filter(and_(Url.type_==Url.NEW_URL, Url.level < 2)).count():
                logger.info(u'Перезапуск генератора задач')
                self.restart_tasks_generator(self.tasks_generator())

        self.save_state(task.request.url, Url.MAP_URL)

    def task_page(self, task, error=None):
        if error:
            logger.error(u'Ошибка при загрузке %s. Повтор.' % task.request.url)
            yield task
            return

        if Page.query.filter_by(url=task.request.url).first():
            logger.error(u'Дублирование задачи для %s!' % task.request.url)
            self.save_state(task.request.url, Url.PAGE_URL)
            return

        item = None

        try:
            content = task.xpath('//div[@id="content"]')

            item = task.structured_xpath(
                '//div[@id="content"]',
                x(
                    './table[4]/tr',
                    class_='./td[1]/text()',
                    group='./td[2]/text()',
                ),
                name_1='.//*[@id="fd_3"]/h2/text()',
                name_2=c('./div[1]/span[3]', apply_func=lambda item: item.text_content()),
                description=c('./div[@id="download_form"]/preceding-sibling::*[preceding-sibling::b[2]]', apply_func=tostring, one=False),
                brand='./h3[1]/text()',
                filetype='./h3[2]/text()',
                filesize='./b[2]/text()',
                image='./a/img/@src'
            )[0]
        except IndexError:
            logger.error(u'Не найдена структура товара на странице %s!' % task.request.url)
        except:
            logger.error(u'Неизвестная ошибка при разборе структуры товара на странице %s!' % task.request.url)

        if not item:
            task.no_cache = True
            yield task
            return

        '''print '%s > %s, %s > %s, %s (%s)  - %s' % (
            item.brand, item.name_1 or item.name_2,
            item.class_, item.group,
            item.filetype, item.filesize,
            task.request.url
        )'''

        item['description'] = ''.join(item.description or [])

        for key, value in item.iteritems():
            if value:
                try:
                    item[key] = value.encode('unicode_escape')
                except:
                    print key, value
                    raise Exception

        page = Page(
            url=task.request.url,
            class_=item.class_ or '',
            group=item.group or '',
            name=item.name_1 or item.name_2 or '',
            type_=item.filetype or '',
            size_=item.filesize or '',
            image_url=item.image or '',
            description=item.description or ''
        )

        database.session.add(page)

        self.save_state(task.request.url, Url.PAGE_URL)


if __name__ == '__main__':
    frontend = Frontend(McgrpRu, connection_string=CONNECTION_STRING)
    frontend.add_view(Url)

    if not WORKER_IN_FRONTEND:
        basicConfig(level=DEBUG)

        #database.drop_all()
        database.create_all()

        McgrpRu.work_type = PREPARE_PAGE

        worker = McgrpRu(
            cache_type=CACHE_RESPONSE,
            #cache_backend=MySQLCacheBackend,
            #cache_database='mysql://root:654321@localhost/fetcher_cache'
            cache_backend=MongoCacheBackend
        )
        worker.start()

        worker.render_stat()
        print '-' * 80
        print u'Количество страниц со списком инструкций: %d' % Url.query.filter(Url.level <= Url.LOOKING).count()
        print u'Количество страниц с инструкциями: %d' % Url.query.filter(Url.level > Url.LOOKING ).count()
        print u'Описаний устройств: %d' % Page.query.count()
        print u'Отсутствующих инструкций (с нулевым размером): %d' % Page.query.filter_by(size_=u'0Б'.encode('unicode_escape')).count()

    else:
        frontend.run()
