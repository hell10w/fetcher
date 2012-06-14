# -*- coding: utf-8 -*-

from logging import getLogger

from fetcher.fetch.temporaryfile import TempFile


logger = getLogger('fetcher.fetch.response')


class Response(object):
    '''Ответ сервера'''

    status_code = None
    url = None
    headers = {}
    cookies = {}

    body = None

    encoding = None
    charset = None

    total_time = None

    is_from_cache = None

    def __init__(self, **kwargs):
        self._content = None
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @property
    def size(self):
        if not self.body:
            return 0
        if isinstance(self.body, TempFile):
            return self.body.size
        else:
            return len(self.body)

    @property
    def content(self):
        '''Возвращает содержимое документа'''
        if not self._content:
            self._content = self.get_unicode_body()
        return self._content

    def get_body(self):
        '''Возвращает тело ответа целиком'''
        if not hasattr(self, '_body'):
            self._body = ''
            for chunk in self.read_body():
                self._body += chunk or ''
        return self._body

    def get_unicode_body(self):
        '''Возвращает тело ответа целиком в utf-8'''
        if not hasattr(self, '_unicode_body'):
            self._unicode_body = self.get_body().decode(self.charset or 'utf-8', 'ignore')
        return self._unicode_body

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

    def setup(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        return self

    def clone(self, **kwargs):
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if key != 'body' and not key.startswith('_')
        )
        return Response(**_kwargs).setup(**kwargs)

    def clone_for_cache(self):
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key.startswith('_')
        )
        return Response(**_kwargs)
