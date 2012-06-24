# -*- coding: utf-8 -*-

from logging import getLogger

from fetcher.utils import import_module


# три вида кэша: выключенный, простое сохранение респонса, настоящий
CACHE_NONE, CACHE_RESPONSE, CACHE_TRUE = range(3)

# Хранение данных осуществляется через наследники от CacheBackend,
# логику кеша реализует CacheExtension


logger = getLogger('fetcher.cache')


class CacheExtension(object):
    '''Расширение паука для реализации разных видов кэша'''

    def __init__(self, cache_type=CACHE_RESPONSE, cache_backend=None, **kwargs):
        '''
            cache_type - тип реализуемого кэша
            cache_backend - имя модуля для импорта класса CacheBackend
        '''
        self._backend = None
        self._cache_type = cache_type
        if self._cache_type != CACHE_NONE and cache_backend:
            if isinstance(cache_backend, str):
                try:
                    cache_backend = import_module('fetcher.cache.%s' % cache_backend).CacheBackend
                except ImportError:
                    logger.error(u'Неудалось импортировать класс реализации кэша! Кэш не будет использоваться!')
            if cache_backend:
                logger.info(u'Использование в качестве кэша %s' % cache_backend)
                self._backend = cache_backend(**kwargs)

    @property
    def is_process_tasks(self):
        '''Если расширение процессит таски возвращает True'''
        return self._backend and self._cache_type != CACHE_NONE

    def process_task(self, task):
        '''Обрабатывает пользовательский таск и по-возможности возвращает таск со старым респонсом'''
        result, error = False, None

        if not task.no_cache_restore:
            # обычное сохранение респонса
            if self._cache_type == CACHE_RESPONSE and self._backend:
                if self._backend.is_exists(task):
                    result, response, error, _, _ = self._backend.get_from_cache(task)
                    if result:
                        response.is_from_cache = True
                        task.response = response

            # TODO: более разумное поведение подобное настоящему браузерному кэшу
            elif self._cache_type == CACHE_TRUE:
                # TODO: оборачивать task в другой task со специальным хэндлером и запрашивать только заголовок
                raise NotImplementedError()

        return result, task, error

    def store_task(self, task, error):
        '''Сохраняет таск ответа на который небыло в кэше'''
        if not task.no_cache_store and self._backend:
            self._backend.set_to_cache(task, error)
