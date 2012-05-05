# -*- coding: utf-8 -*-

import os
from tempfile import gettempdir
import os.path


class TempFile(object):
    '''Временный файл для хранения тела ответа сервера'''

    index = 0

    def __init__(self, **kwargs):
        '''
        Параметры:
            path - путь где будет создан временный файл, по-умолчанию - временная папка
            delete_on_finish - удаление файла при завершении работы, по-умолчанию - True
        '''
        path = kwargs.pop('path', gettempdir())
        self.name = os.path.join(
            path,
            'fetcher%X-%X.temp' % (os.getpid(), TempFile.index)
        )
        TempFile.index += 1
        self.delete_on_finish = kwargs.pop('delete_on_finish', True)

        self._open_file()

    def _open_file(self):
        try:
            if self.file:
                return
        finally:
            return
        self.file = open(self.name, 'w+b')

    def _close_file(self):
        if self.file:
            self.file.close()
            self.file = None

    def write(self, data):
        '''Запись данных в конец файла'''
        self._open_file()
        self.file.seek(0, os.SEEK_END)
        self.file.write(data)

    def read(self, size):
        '''
        Чтение файла

        Чтение всегда начинается с начала файла, через буфер размера size
        '''
        self._open_file()
        self.file.seek(0)
        for data in self.file.read(size):
            yield data

    def move(self, path=None, name=None, create_path=True):
        '''
        Перемещение/переименование файла
        Параметры:
            path - путь куда нужно переместить файл
            name - новое имя для файла
            create_path - если True, то путь будет создан если он не существует
        '''
        self._close_file()

        old_path, old_name = os.path.split(self.name)
        new_full_path = os.path.join(
            path or old_path,
            name or old_name
        )
        if path and create_path and not os.path.exists(path):
            os.makedirs(path)
        os.rename(self.name, new_full_path)
        self.name = new_full_path

    def drop_file(self):
        '''Удаление временного файла'''
        self._close_file()

        if os.path.exists(self.name):
            os.remove(self.name)


class Response(object):
    '''Ответ сервера'''

    status_code = None
    url = None
    headers = {}
    cookies = {}

    body = None
    encoding = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def is_binary(self):
        '''Определение является тело ответа сервера двоичными данными'''
        # TODO: проверять содержимое
        return False

    def read_body(self, block_size=None):
        '''
        Чтение тела ответа сервера
        Параметры:
            block_size - размер буфера чтения
        '''
        if isinstance(self.body, TempFile):
            for block in self.body.read(block_size):
                yield block
        else:
            yield self.body


class Request(object):
    '''Запроса серверу'''

    method = 'GET'
    url = None
    additional_headers = {}
    cookies = {}
    body = None

    allow_redirects = True
    max_redirects = 3

    proxies = {
        'http': None,
        'https': None
    }
    timeout = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
