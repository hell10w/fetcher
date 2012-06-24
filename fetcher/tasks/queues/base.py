# -*- coding: utf-8 -*-

class BaseQueue(object):
    def size(self):
        '''Возвращает размер очереди'''
        raise NotImplementedError

    def get(self):
        '''Извлекает из очереди пару (приоритет, задача)'''
        raise NotImplementedError

    def put(self, item):
        '''Помещает в очередь пару (приоритет, задача)'''
        raise NotImplementedError
