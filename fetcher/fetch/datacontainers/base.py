# -*- coding: utf-8 -*-


class BaseDataContainer(object):
    def size(self):
        '''Возвращает размер данных в контейнере'''
        return 0

    def write(self, data):
        '''Записывает данные в конец контейнера'''
        pass

    def read(self, size=None):
        '''
        Читает данные из контейнера
        Если size=None, то возвращает данные целиком, иначе - возвращает генератор читающий по size байт
        '''
        if not size:
            return None
        else:
            return self.read_iterator(size)

    def read_iterator(self, size):
        '''Итератор данных в контейнере, порциями по size байт'''
        yield None

    def validate(self):
        '''Проверяет целостность данных'''
        return True
