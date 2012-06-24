# -*- coding: utf-8 -*-

class BaseCacheBackend(object):
    def is_exists(self, task):
        '''Возвращает True только если ответ на такой url есть в кэше'''
        return False

    def get_from_cache(self, task):
        '''Извлекает из кэша таск'''
        # флаг - удалось ли найти что-то
        # response
        # error
        # дата помещения в кэш
        # дополнительные данные в словере
        return False, None, None, None, None

    def set_to_cache(self, task, error, additional=None):
        '''Сохраняет в кэш таск если может'''
