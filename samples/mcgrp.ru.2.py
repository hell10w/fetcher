# -*- coding: utf-8 -*-

import os
import os.path
import logging

from pymongo import Connection

from lxml.html import tostring
from werkzeug.urls import url_fix
from sqlalchemy.sql.expression import or_, not_, and_

from fetcher import MultiFetcher, MongoCacheBackend, CACHE_RESPONSE, Task, Structure as x, Chunk as c, Request, MEMORY_RESPONSE_BODY
from fetcher.frontend.flask_frontend import Frontend, app, database, model


Request.body_destination = MEMORY_RESPONSE_BODY


logger = logging.getLogger('fetcher.worker')


class McgrpRu(MultiFetcher):
    MAP_LOAD, INFO_LOAD, IMAGES_LOAD = range(3)
    NEW_URL, LOADING_URL, MAP_URL, PAGE_URL, IMAGE_URL = range(5)

    stage = MAP_LOAD

    initial_url = 'http://mcgrp.ru'
    images_save_path = '/home/alex/projects/McgrpRu-Images/'

    def __init__(self, *args, **kwargs):
        #
        connection = Connection()
        database = connection['McgrpRu']

        self.map_urls = database['map_urls']
        self.page_urls = database['page_urls']

        #
        if not os.path.exists(self.images_save_path):
            os.mkdir(self.images_save_path)

        #
        if self.stage == self.MAP_LOAD:
            url = url_fix(unicode(self.initial_url))
            if not self.map_urls.find_one({'url': url}):
                self.map_urls.insert(
                    {
                        'url': url,
                        'level': 0,
                        'type': self.NEW_URL
                    }
                )

        #
        super(McgrpRu, self).__init__(*args, **kwargs)


    def tasks_generator(self):
        if self.stage == self.MAP_LOAD:
            urls = list(self.map_urls.find({'type': self.LOADING_URL, 'level': {'$lte': 1}}))
            if urls:
                logger.info(u'В прошлой сессии прервана загрузка %d страниц!' % len(urls))
            else:
                urls = list(self.map_urls.find({'type': self.NEW_URL, 'level': {'$lte': 1}}, limit=30))

            while True:
                if not urls:
                    break
                for url in urls:
                    self.map_urls.update({'url': url['url']}, {'$set': {'type': self.LOADING_URL}})
                    yield Task(
                        handler='map',
                        level=url['level'],
                        url=url['url']
                    )
                urls = list(self.map_urls.find({'type': self.NEW_URL, 'level': {'$lte': 1}}, limit=30))

        logger.info(u'Страницы для проверки закончились!')

    def task_map(self, task, error=None):
        location = url_fix(unicode(task.request.url))

        if error:
            logger.error(u'Ошибк при загрузке страницы %s' % location)
            task.no_cache_restore = True
            yield task
            return

        try:
            task.make_links_absolute()

            urls = task.xpath_list(
                '//a/@href',
                filter=lambda url: url.startswith('http://mcgrp.ru/')
            )

            urls = set(urls)
            urls = map(
                lambda url: url_fix(unicode(url)),
                urls
            )

            for url in urls:
                if not self.map_urls.find_one({'url': url}):
                    self.map_urls.insert(
                        {
                            'url': url,
                            'level': task.level + 1,
                            'type': self.NEW_URL
                        }
                    )

        except:
            logger.error(u'Неизвестная ошибка при извлечении ссылок со страницы %s' % location)
            task.no_cache_restore = True
            yield task
            return

        try:
            self.map_urls.update({'url': location}, {'$set': {'type': self.MAP_URL}})
        except:
            logger.error(u'Ошибка при сохранении состояния страницы %s' % location)

        if not self.tasks_generator_enabled:
            if self.map_urls.find_one({'type': self.NEW_URL, 'level': {'$lte': 1}}):
                logger.info(u'Перезапуск генератора задач')
                self.restart_tasks_generator(self.tasks_generator())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    worker = McgrpRu(cache_type=CACHE_RESPONSE, cache_backend=MongoCacheBackend)
    worker.start()

    worker.render_stat()
