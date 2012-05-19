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

    def get_body(self):
        '''Возвращает тело ответа целиком'''
        body = ''
        for chunk in self.read_body():
            body += chunk or ''
        return body

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

    def browse(self):
        '''Открывает в браузере документ'''

        # TODO: это
        #fh, path = tempfile.mkstemp()
        #self.save(path)
        #webbrowser.open('file://' + path)

    def clone(self):
        kargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key.startswith('_') and key != 'body'
        )
        return Response(**kargs)
