# -*- coding: utf-8 -*-

from logging import getLogger
from zlib import compress, decompress
from time import time
from cPickle import dumps, loads

from sqlalchemy import create_engine, Column, Integer, Text, BLOB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from base import CacheBackend


logger = getLogger('fetcher.cache.mysqlcache')


Session = sessionmaker()
Base = declarative_base()


class CacheItem(Base):
    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True)

    url = Column(Text)
    data = Column(BLOB)


class MySQLCacheBackend(CacheBackend):
    '''Реализация для хранения кэша в mongo'''

    def __init__(self, cache_database=None, *args, **kwargs):
        if not cache_database:
            raise Exception(u'Необходимо указать строку для подключения к БД!')

        engine = create_engine(cache_database)
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)

        self.session = Session()

    def is_exists(self, task):
        '''Возвращает True только если ответ на такой url есть в кэше'''
        return self.session.query(CacheItem).filter_by(url=task.request.url).first()

    def get_from_cache(self, task):
        '''Извлекает из кэша таск'''

        result, response, error, time, additional = False, None, None, None, None

        item = self.session.query(CacheItem).filter_by(url=task.request.url).first()

        if item:
            data = item.data
            if data:
                try:
                    data = loads(decompress(data))

                    response = data.get('response', None)
                    error = data.get('error', None)
                    time = data.get('time', None)
                    additional = data.get('additional', None)

                    result = True

                except:
                    # TODO: обрабатывать что-то конкетное - пока на всем валится
                    logger.error(u'Произошла ошибка при извлечении из кэша результата для %s' % task.request.url)

        return result, response, error, time, additional

    def set_to_cache(self, task, error, additional=None):
        '''Сохраняет в кэш таск если может'''

        url = task.request.url
        data = {
            'response': task.response.clone_for_cache(),
            'error': error,
            'additional': additional,
            'time': time()
        }

        item = self.session.query(CacheItem).filter_by(url=url).first()

        if item:
            item.data = data

        else:
            store_item = CacheItem(
                url=url,
                data=compress(dumps(data))
            )

            self.session.add(store_item)

        self.session.commit()
