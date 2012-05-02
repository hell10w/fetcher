# -*- coding: utf-8 -*-

from tempfile import NamedTemporaryFile


class TempFile(object):
    '''Временный файл для хранения тела ответа сервера'''

    def __init__(self):
        self.file = NamedTemporaryFile(prefix='fetcher', delete=False)


class Response(object):
    '''Класс ответа сервера'''

    status_code = None
    url = None
    headers = {}
    cookies = {}
    body = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class Request(object):
    '''Класс для хранения запроса серверу'''

    method = 'get'
    url = None
    additional_headers = {}
    body = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
