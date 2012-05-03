# -*- coding: utf-8 -*-

from tempfile import NamedTemporaryFile


class TempFile(object):
    '''Временный файл для хранения тела ответа сервера'''

    def __init__(self):
        self.file = NamedTemporaryFile(prefix='fetcher', delete=False)
        self.name = self.file.name
        self.file.close()


class Response(object):
    '''Ответ сервера'''

    status_code = None
    url = None
    headers = {}
    cookies = {}
    body = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


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
