# -*- coding: utf-8 -*-

from fetcher.fetch.temporaryfile import TempFile


class Response(object):
    '''Ответ сервера'''

    status_code = None
    url = None
    headers = {}
    cookies = {}

    body = None

    encoding = None

    total_time = None

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

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
