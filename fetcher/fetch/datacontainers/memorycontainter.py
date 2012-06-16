# -*- coding: utf-8 -*-

from base import BaseDataContainer


class MemoryContainer(BaseDataContainer):
    def __init__(self, *args, **kwargs):
        self._data = []

    def size(self):
        '''Возвращает размер данных в контейнере'''
        return sum([len(block) for block in self._data])

    def write(self, data):
        '''Записывает данные в конец контейнера'''
        self._data.append(data)

    def read(self, size=None):
        '''
        Читает данные из контейнера
        Если size=None, то возвращает данные целиком, иначе - возвращает генератор читающий по size байт
        '''
        if not size:
            return ''.join(self._data)
        else:
            return self.read_iterator(size)

    def read_iterator(self, size):
        '''Итератор данных в контейнере, порциями по size байт'''
        # TODO: генерировать частями
        for block in self._data:
            yield block
