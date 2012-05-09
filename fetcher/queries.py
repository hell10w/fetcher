# -*- coding: utf-8 -*-

from fetcher.temporaryfile import TempFile
from fetcher.useragents import get_user_agent


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
    user_agent = get_user_agent()
    cookies = {}
    body = None

    allow_redirects = True
    max_redirects = 3

    proxies = {
        'http': None,
        'https': None
    }
    connection_timeout = None
    timeout = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
