# -*- coding: utf-8 -*-

from os import SEEK_END, getpid, makedirs
from os.path import join, split, exists, getsize
from time import time
from tempfile import gettempdir

from base import BaseDataContainer


class FileContainer(BaseDataContainer):
    _index = 0

    def __init__(self, filename=None, *args, **kwargs):
        self._file = None

        self._filename = filename or join(
            gettempdir(),
            'fetcher',
            '%X-%X' % (getpid(), FileContainer._index / 1000),
            '%X.dat' % FileContainer._index
        )

        path, _ = split(self._filename)
        if not exists(path):
            makedirs(path)

        FileContainer._index += 1

    def __del__(self):
        self._close_file()

    def size(self):
        '''Возвращает размер данных в контейнере'''
        return getsize(self._filename)

    def write(self, data):
        '''Записывает данные в конец контейнера'''
        self._open_file()
        self._file.seek(0, SEEK_END)

        self._file.write(data)

    def read(self, size=None):
        '''
        Читает данные из контейнера
        Если size=None, то возвращает данные целиком, иначе - возвращает генератор читающий по size байт
        '''
        self._open_file()
        self._file.seek(0)

        if not size:
            return self._file.read()
        else:
            return self.read_iterator(size)

    def validate(self):
        '''Проверяет целостность данных'''
        return exists(self._filename)

    def read_iterator(self, size):
        '''Итератор данных в контейнере, порциями по size байт'''
        while True:
            data = self._file.read(size)
            if data:
                yield data
            else:
                break

    def _open_file(self):
        if isinstance(self._file, file):
            return
        self._file = open(self._filename, 'a+b')

    def _close_file(self):
        if not isinstance(self._file, file):
            return
        self._file.close()
        self._file = None

    def __getstate__(self):
        self._close_file()
        return {'filename': self._filename}

    def __setstate__(self, state):
        self._file = None
        self._filename = state['filename']
