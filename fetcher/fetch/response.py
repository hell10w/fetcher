# -*- coding: utf-8 -*-

from logging import getLogger
from os import fdopen
from tempfile import mkstemp

from datacontainers import FileContainer, MemoryContainer
from request import MEMORY_RESPONSE_BODY, FILE_RESPONSE_BODY, AUTO_RESPONSE_BODY


logger = getLogger('fetcher.fetch.response')


class Response(object):
    '''Ответ сервера'''

    def __init__(self, **kwargs):
        self.status_code = None
        self.url = None
        self.headers = {}
        self.cookies = {}

        self.body = None

        self.encoding = None
        self.charset = None

        self.total_time = None

        self.is_from_cache = None

        self.setup(**kwargs)

    def setup(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        return self

    @property
    def size(self):
        if not self.body:
            return 0
        return self.body.size()

    def clone(self, **kwargs):
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key[0] == '_'
        )
        return Response(**kwargs).setup(**_kwargs)

    @property
    def raw_content(self):
        '''Возвращает содержимое документа как есть'''
        if not hasattr(self, '_raw_body'):
            if self.body:
                self._raw_body = self.body.read()
            else:
                self._raw_body = ''
                logger.debug(u'Не построено тело ответа для %s' % self.url)
        return self._raw_body

    @property
    def content(self):
        '''Возвращает содержимое документа'''
        if not hasattr(self, '_body'):
            if self.body:
                self._body = self.body.read()
                self._body = self._body.decode(self.charset or 'utf-8', 'ignore')
            else:
                self._body = ''
                logger.debug(u'Не построено тело ответа для %s' % self.url)
        return self._body

    def dump_content(self, filename=None, suffix='.dat', prefix='response'):
        '''Сохраняет ответ сервера во временный файл или в файл с указанным именем'''
        if filename:
            f = open(filename, 'wb')
        else:
            handle, filename = mkstemp(suffix=suffix, prefix=prefix)
            f = fdopen(handle, 'wb')
        try:
            f.write(self.raw_content)
        finally:
            f.close()
        return filename

    def _rather_file_destination(self):
        '''Определяет предпочтительность сохранения ответа сервера в файл'''

        content_type = self.headers.get('Content-Type', [None])[0]
        if content_type:
            if content_type.startswith('text/'):
                return False

        content_length = int(self.headers.get('Content-Length', [None])[0] or 0)
        if content_length < 1024 * 1024:
            return False

        return True

    def _setup_body(self, destination, *args, **kwargs):
        '''Устанавливает место назначение ответа сервера'''

        if destination == AUTO_RESPONSE_BODY:
            if self._rather_file_destination():
                destination = FILE_RESPONSE_BODY
            else:
                destination = MEMORY_RESPONSE_BODY

        if destination == FILE_RESPONSE_BODY:
            self.body = FileContainer(*args, **kwargs)

        elif destination == MEMORY_RESPONSE_BODY:
            self.body = MemoryContainer(*args, **kwargs)
