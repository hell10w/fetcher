# -*- coding: utf-8 -*-

from fetcher.fetch.request import MEMORY_RESPONSE_BODY, FILE_RESPONSE_BODY, AUTO_RESPONSE_BODY
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

    def _process_headers(self):
        '''Объединение заголовков ответа в словарь'''
        # если это уже сделано - выход
        if self.headers:
            return
        # если частей нет - выход
        self.headers = {}
        if not self.header_chunks:
            return
        # обход пока не код ответа
        for line in self.header_chunks[::-1]:
            line = line.strip()
            if line.startswith('HTTP/'):
                break
            elif line:
                key, value = line.split(': ', 1)
                self.headers.setdefault(key, []).append(value)

    def _presumably_binary_body(self):
        '''Определение двоичен ли ответ сервера исходя из заголовков ответа'''
        content_type = self.headers.get('Content-Type', [None])[0]
        if content_type:
            if content_type.startswith('text/'):
                return False
        #content_length = int(self.headers.get('Content-Length', [None])[0] or 0)
        #if content_length < 1024 * 1024:
        #    return False
        return True

    def _setup_body_destination(self, destination):
        '''Устанавливает параметры для записи тела ответа сервера'''
        self._write_function = lambda chunk: None

        if destination == FILE_RESPONSE_BODY:
            self.body = TempFile()
            self._write_function = self.body.write

        elif destination == MEMORY_RESPONSE_BODY:
            self.body = []
            self._write_function = lambda chunk: self.body.append(chunk)

    def _writer(self, chunk):
        '''Обработчик фрагметов тела ответа сервера'''
        # если место назначения не сконфигурировано
        if not self.body:
            destination = self._destination
            if destination == AUTO_RESPONSE_BODY:
                # получаем заголовки
                self._process_headers()
                # определяем бинарно ли содержимое
                if self._presumably_binary_body():
                    destination = FILE_RESPONSE_BODY
                else:
                    destination = MEMORY_RESPONSE_BODY
            self._setup_body_destination(destination)
        # запись фрагмента
        self._write_function(chunk)
