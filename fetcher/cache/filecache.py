# -*- coding: utf-8 -*-

from os import mkdir
from os.path import exists, join
from logging import getLogger
from zlib import compress, decompress
from time import time
from cPickle import dumps, loads
from base64 import urlsafe_b64encode, urlsafe_b64decode

from base import CacheBackend


logger = getLogger('fetcher.cache.filecache')


class FileCacheBackend(CacheBackend):
    '''Реализация для хранения кэша в mongo'''

    def __init__(self, cache_path=None, *args, **kwargs):
        self._cache_path = cache_path
        if not exists(cache_path):
            mkdir(cache_path)

    def _file_name(self, url):
        return join(
            self._cache_path,
            urlsafe_b64encode(url)
        )

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

                    result = True

                except:
                    # TODO: обрабатывать что-то конкетное - пока на всем валится
                    logger.error('Произошла ошибка при извлечении из кэша результата для %s' % task.request.url)

                    #else:
                    #    result = True

        return result, response, error, time, additional

    def set_to_cache(self, task, error, additional=None):
        '''Сохраняет в кэш таск если может'''

        filename = self._file_name(task.request.url)

        data = {
            'response': task.response.clone_for_cache(),
            'error': error,
            'additional': additional,
            'time': time()
        }

        with open(filename, 'wb') as f:
            f.write(compress(dumps(data)))
