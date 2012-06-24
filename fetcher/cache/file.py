# -*- coding: utf-8 -*-

from os import makedirs
from os.path import exists, join
from logging import getLogger
from zlib import compress, decompress
from time import time
from cPickle import dumps, loads
from urllib import quote
from tempfile import gettempdir

from base import BaseCacheBackend


logger = getLogger('fetcher.cache.file')


class CacheBackend(BaseCacheBackend):
    '''Реализация для хранения кэша в файлах в директории'''

    def __init__(self, cache_path=None, *args, **kwargs):
        self._cache_path = cache_path or join(gettempdir(), 'fetcher-cache')
        if not exists(self._cache_path):
            makedirs(self._cache_path)

    def _file_name(self, url):
        url = url.rstrip('/')
        if '://' in url:
            url = url.split('://')[1]
        url = quote(url)
        full_path = url.split('/')

        path = join(self._cache_path, *full_path[:-1])
        if not exists(path):
            makedirs(path)

        return join(path, full_path[-1] + '.dat')

    def is_exists(self, task):
        '''Возвращает True только если ответ на такой url есть в кэше'''
        return exists(self._file_name(task.request.url))

    def get_from_cache(self, task):
        '''Извлекает из кэша таск'''

        result, response, error, time, additional = False, None, None, None, None

        filename = self._file_name(task.request.url)

        with open(filename, 'rb') as f:
            data = f.read()

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

        return result, response, error, time, additional

    def set_to_cache(self, task, error, additional=None):
        '''Сохраняет в кэш таск если может'''

        filename = self._file_name(task.request.url)

        data = {
            'response': task.response.clone(),
            'error': error,
            'additional': additional,
            'time': time()
        }

        with open(filename, 'wb') as f:
            f.write(compress(dumps(data)))
