# -*- coding: utf-8 -*-

from time import time
from cPickle import dumps, loads

from pymongo import Connection, ASCENDING
from pymongo.binary import Binary


CACHE_NONE, CACHE_RESPONSE, CACHE_TRUE = range(3)


class CacheExtension(object):
    def __init__(self, cache_type=CACHE_NONE, cache_database=None, **kwargs):
        self._cache_type = cache_type

        if self.is_process_tasks:
            connection = Connection()
            database = connection[cache_database or 'FetcherCache']
            self._collection = database['cache']

    @property
    def is_process_tasks(self):
        return self._cache_type not in [CACHE_NONE]

    def _get_from_cache(self, task):
        result, error = False, None
        if self._cache_type == CACHE_RESPONSE:
            item = self._collection.find_one({'url': task.request.url})
            if item:
                response = item.get('response', None)
                if response:
                    task.response = loads(response)
                    task.response.is_from_cache = True
                error = item.get('error', None)
                if error:
                    error = loads(error)
                result = True
        elif self._cache_type == CACHE_TRUE:
            raise NotImplementedError()
        return result, task, error

    def _set_to_cache(self, task, error):
        if self._cache_type == CACHE_RESPONSE:
            item = self._collection.find_one({'url': task.request.url})
            if not item:
                new_response = [
                    {
                        'url': task.request.url,
                        'response': Binary(dumps(task.response.clone_for_cache())),
                        'error': None if not error else Binary(dumps(error)),
                        'stored': time()
                    }
                ]
                self._collection.insert(new_response)
        elif self._cache_type == CACHE_TRUE:
            raise NotImplementedError()

    def process_task(self, task):
        '''Обрабатывает пользовательский таск и по-возможности возвращает старый'''
        result, error = False, None

        if not task.no_cache:
            if self._cache_type == CACHE_RESPONSE:
                result, stored_task, stored_error = self._get_from_cache(task)
                if result:
                    task, error = stored_task, stored_error

            elif self._cache_type == CACHE_TRUE:
                raise NotImplementedError()
                #task.cache_data = TaskCacheData()
                #task.cache_data.old_handler = task.handler
                #task.handler = '__cache'

        return result, task, error

    def store_task(self, task, error):
        '''Сохраняет таск ответа на который небыло в кэше'''
        if not task.no_cache:
            self._set_to_cache(task, error)
