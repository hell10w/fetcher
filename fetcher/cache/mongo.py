# -*- coding: utf-8 -*-

from logging import getLogger
from zlib import compress, decompress
from time import time
from cPickle import dumps, loads

from pymongo import Connection
from pymongo.binary import Binary

from base import BaseCacheBackend


logger = getLogger('fetcher.cache.mongo')


class CacheBackend(BaseCacheBackend):
    '''Реализация для хранения кэша в mongo'''

    def __init__(self, cache_database=None, *args, **kwargs):
        connection = Connection()
        database = connection[cache_database or 'FetcherCache']
        self._collection = database['cache']

    def is_exists(self, task):
        '''Возвращает True только если ответ на такой url есть в кэше'''
        search_key = {'url': task.request.url}
        return self._collection.find_one(search_key)

    def get_from_cache(self, task):
        '''Извлекает из кэша таск'''

        result, response, error, time, additional = False, None, None, None, None

        search_key = {'url': task.request.url}
        item = self._collection.find_one(search_key)

        if item:
            data = item.get('data', None)
            if data:
                try:
                    data = loads(decompress(data))

                    response = data.get('response', None)
                    error = data.get('error', None)
                    time = data.get('time', None)
                    additional = data.get('additional', None)

                    result = response.body.validate()

                except:
                    # TODO: обрабатывать что-то конкетное - пока на всем валится
                    logger.error('Произошла ошибка при извлечении из кэша результата для %s' % task.request.url)

                #else:
                #    result = True

        return result, response, error, time, additional

    def set_to_cache(self, task, error, additional=None):
        '''Сохраняет в кэш таск если может'''

        search_key = {'url': task.request.url}

        item = self._collection.find_one(search_key)

        if not item:
            url = task.request.url
            data = {
                'response': task.response.clone(),
                'error': error,
                'additional': additional,
                'time': time()
            }

            store_item = {
                'url': url,
                'data': Binary(compress(dumps(data)))
            }

            self._collection.insert(store_item)
