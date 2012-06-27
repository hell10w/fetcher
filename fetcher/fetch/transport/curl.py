# -*- coding: utf-8 -*-

from logging import getLogger
from urlparse import urljoin
from StringIO import StringIO
from Cookie import SimpleCookie, CookieError
from urlparse import parse_qsl
from urllib import quote, urlencode

import pycurl

from fetcher.fetch.extensions.forms_ext import PostFile
from fetcher.fetch.transport.base import BaseFetcher
from fetcher.fetch.response import Response


logger = getLogger('fetcher.curl')


class CurlFetcher(BaseFetcher):
    '''Транспорт для запросов на библиотеке Curl'''

    def __init__(self, **kwarg):
        super(CurlFetcher, self).__init__()

    def prepare_from_task(self, task, **kwargs):
        '''Подготавливает запрос из задачи'''

        curl = kwargs.get('curl', None)

        # основные настройки
        curl.setopt(pycurl.USERAGENT, task.request.user_agent or '')

        # HTTPS в топку
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        # редиректы
        curl.setopt(pycurl.FOLLOWLOCATION, int(task.request.allow_redirects))
        curl.setopt(pycurl.MAXREDIRS, task.request.max_redirects)

        # задержки
        curl.setopt(pycurl.CONNECTTIMEOUT, task.request.connection_timeout or 0)
        curl.setopt(pycurl.TIMEOUT, task.request.overall_timeout or 0)

        # имя метода
        task.request.method = task.request.method.upper()

        # TODO: после настройки curl все задействованые параметры из task.request должны быть удалены

        # метод
        if task.request.method == 'GET':
            curl.setopt(pycurl.HTTPGET, 1)
            if task.request.post:
                task.request.url = task.request.url + '?' + urlencode(task.request.post)
        elif task.request.method == 'POST':
            curl.setopt(pycurl.POST, 1)
            # POST
            if task.request.post:
                if task.request.is_multipart_post:
                    _post = [
                        (key, self._process_for_post_file(value))
                        for key, value in task.request.post
                    ]
                    curl.setopt(pycurl.HTTPPOST, _post)
                else:
                    curl.setopt(pycurl.POSTFIELDS, task.request.post)
            else:
                curl.setopt(pycurl.POSTFIELDS, '')
        elif task.request.method == 'PUT':
            curl.setopt(pycurl.PUT, 1)
            if task.request.post:
                if isinstance(task.request.post, file):
                    read_function = task.request.post.read
                else:
                    read_function = StringIO(task.request.post).read
                task.request.post = None
            curl.setopt(pycurl.READFUNCTION, read_function)
            # TODO: проверить PUT-метод для файлов и всего остального
        elif task.request.method == 'DELETE':
            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        elif task.request.method == 'HEAD':
            curl.setopt(pycurl.NOBODY, 1)
        elif task.request.method == 'UPLOAD':
            curl.setopt(pycurl.UPLOAD, 1)

        # URL
        # TODO: тут все через задницу
        url = task.request.url
        if url:
            if not url[:7].lower().startswith('http://'):
                url = urljoin(task.response.url, url)
        if not isinstance(url, (str, unicode)):
            raise TypeError(u'Неправильный тип URL: %s' % type(url))
        if isinstance(url, unicode):
            try:
                url = str(url.decode('utf-8'))
            except UnicodeEncodeError:
                url = str(quote(url, safe=':/&?.:='))
        curl.setopt(pycurl.URL, url)

        if 'zlib' in pycurl.version:
            curl.setopt(pycurl.ENCODING, 'gzip')

        # реферер
        curl.setopt(pycurl.REFERER, task.request.referer or '')

        # дополнительные заголовки
        curl.setopt(
            pycurl.HTTPHEADER,
            [
                '%s: %s' % item
                for item in task.request.additional_headers.iteritems()
            ]
        )

        # куки
        if task.request.cookies:
            try:
                cookies = SimpleCookie(task.request.cookies)
                curl.setopt(pycurl.COOKIELIST, 'ALL')
                curl.setopt(
                    pycurl.COOKIELIST,
                    'Set-Cookie: %s' % cookies.output(header='', sep=';')
                )
            except CookieError:
                logger.error(u'Ошибка при разборе кук парсером!')
        else:
            curl.setopt(pycurl.COOKIEFILE, '')

        # прокси
        curl.setopt(pycurl.PROXY, '')

        if task.request.proxy:
            curl.setopt(pycurl.PROXY, task.request.proxy)
            proxy_type = task.request.proxy_type or 'HTTP'
            proxy_type = getattr(pycurl, 'PROXYTYPE_%s' % proxy_type.upper())
            curl.setopt(pycurl.PROXYTYPE, proxy_type)
            curl.setopt(pycurl.PROXYUSERPWD, task.request.proxy_auth or '')

        # сборщик заголовков
        task.response = CurlResponse(debug=task.debug)
        curl.setopt(pycurl.HEADERFUNCTION, task.response.header_chunks.append)

        # коллектор тела ответа сервера
        task.response._destination = task.request.body_destination
        task.response._container_options = task.request.container_options or {}
        curl.setopt(pycurl.WRITEFUNCTION, task.response._writer)

        # отладка
        curl.setopt(pycurl.VERBOSE, 1 if task.debug else 0)
        curl.setopt(
            pycurl.DEBUGFUNCTION,
            task.response._debug_logger if task.debug else lambda _type, text: None
        )

    def process_to_task(self, task, **kwargs):
        '''Возвращает результат выполнения запроса в задачу'''
        #raise NotImplementedError

        # применение параметров из ответа на запрос к таску, чтобы
        # можно было использовать в дальнейшем, например, куки

        curl = kwargs.get('curl', None)

        task.response._process_headers()

        task.response.total_time = curl.getinfo(pycurl.TOTAL_TIME)
        task.response.url = curl.getinfo(pycurl.EFFECTIVE_URL)
        task.response.status_code = curl.getinfo(pycurl.HTTP_CODE)

        cookies = {}
        for line in curl.getinfo(pycurl.INFO_COOKIELIST):
            chunks = line.split('\t')
            cookies[chunks[-2]] = chunks[-1]
        task.response.cookies = cookies

        task.process_response()

    def _process_for_post_file(self, value):
        if isinstance(value, PostFile):
            if value._content_type:
                content_type = (pycurl.FORM_CONTENTTYPE, value._content_type)
            else:
                content_type = ()
            if value._file_content:
                contents = (pycurl.FORM_CONTENTS, value._file_content)
            elif value._filename:
                contents = (pycurl.FORM_FILE, value._filename)
            return content_type + contents

        else:
            return value


class CurlResponse(Response):
    '''Curl-специфичная часть класса ответа сервера'''

    def __init__(self, debug=False, *args, **kwargs):
        self.header_chunks = []
        if debug:
            self._collected_headers_in = []
            self._collected_headers_out = []
            self._collected_data_out = []
        self.debug = debug
        super(CurlResponse, self).__init__(*args, **kwargs)

    def _process_headers(self):
        '''Объединение заголовков ответа в словарь'''

        # если это уже сделано - выход
        if self.headers:
            return

        if self.debug:
            logger.debug(u'Исходящие заголовки:\n' + '\n'.join(self._collected_headers_out))
            if self._collected_data_out:
                logger.debug(u'Исходящие данные:\n' + '\n'.join(self._collected_data_out))
            logger.debug(u'Входящие заголовки:\n' + '\n'.join(self._collected_headers_in))

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
                try:
                    key, value = line.split(': ', 1)
                    self.headers.setdefault(key, []).append(value)
                except:
                    pass

        # определение и установка кодировки
        content_type = self.headers.get('Content-Type', [None])[0]
        if content_type:
            items = dict((key.strip(), value) for key, value in parse_qsl(content_type))
            charset = items.get('charset', None)
            if charset:
                try:
                    u'x'.encode(charset)
                except LookupError:
                    pass
                else:
                    self.charset = charset

    def _writer(self, chunk):
        '''Обработчик фрагметов тела ответа сервера'''

        # если место назначения не сконфигурировано
        if not self.body:
            self._process_headers()
            self._setup_body(self._destination, **self._container_options)

        # запись фрагмента
        self.body.write(chunk)

    def _debug_logger(self, type, text):
        '''Обрабатывает отладочные сообщения от curl'''

        if type == pycurl.INFOTYPE_TEXT:
            logger.debug(text.rstrip())

        elif type == pycurl.INFOTYPE_HEADER_IN:
            self._collected_headers_in.append(text.rstrip())

        elif type == pycurl.INFOTYPE_HEADER_OUT:
            self._collected_headers_out.append(text.rstrip())

        elif type == pycurl.INFOTYPE_DATA_OUT:
            self._collected_data_out.append(text.rstrip())
