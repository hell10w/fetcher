# -*- coding: utf-8 -*-

from urllib import urlencode
from StringIO import StringIO
from Cookie import SimpleCookie

import pycurl

from fetcher.fetch.request import MEMORY_RESPONSE_BODY, FILE_RESPONSE_BODY, AUTO_RESPONSE_BODY
from fetcher.fetch.temporaryfile import TempFile
from fetcher.fetch.transport.base import BaseFetcher


class CurlFetcher(BaseFetcher):
    '''Транспорт для запросов на библиотеке Curl'''

    def __init__(self, **kwarg):
        super(CurlFetcher, self).__init__()

    def prepare_from_task(self, task, **kwargs):
        '''Подготавливает запрос из задачи'''

        curl = kwargs.get('curl', None)

        curl.setopt(pycurl.USERAGENT, task.request.user_agent or '')

        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        curl.setopt(pycurl.VERBOSE, 0)
        curl.setopt(pycurl.DEBUGFUNCTION, lambda _type, text: None)

        curl.setopt(pycurl.FOLLOWLOCATION, int(task.request.allow_redirects))
        curl.setopt(pycurl.MAXREDIRS, task.request.max_redirects)

        curl.setopt(pycurl.CONNECTTIMEOUT, task.request.connection_timeout or 0)
        curl.setopt(pycurl.TIMEOUT, task.request.overall_timeout or 0)

        curl.setopt(pycurl.URL, task.request.url)

        task.request.method = task.request.method.upper()

        # TODO: после настройки curl все задействованые параметры из task.request должны быть удалены
        # TODO: конфигурирование task.request.post и task.request.url дожно делать в расширении ответственном за формы

        if task.request.post:
            if not task.request.is_multipart_post:
                curl.setopt(pycurl.POSTFIELDS, task.request.post or '')
            else:
                curl.setopt(pycurl.HTTPPOST, task.request.post or '')

        if task.request.method == 'GET':
            curl.setopt(pycurl.HTTPGET, 1)
        elif task.request.method == 'POST':
            curl.setopt(pycurl.POST, 1)
            # TODO: проверить POST
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

        if 'zlib' in pycurl.version:
            curl.setopt(pycurl.ENCODING, 'gzip')

        curl.setopt(pycurl.REFERER, task.request.referer or '')

        curl.setopt(
            pycurl.HTTPHEADER,
            [
                '%s: %s' % item
                for item in task.request.additional_headers.iteritems()
            ]
        )

        curl.setopt(pycurl.COOKIEFILE, '')

        if task.request.cookies:
            cookies = SimpleCookie(task.request.cookies)
            curl.setopt(pycurl.COOKIELIST, 'ALL')
            curl.setopt(
                pycurl.COOKIELIST,
                'Set-Cookie: %s' % cookies.output(header='', sep=';')
            )

        if not task.request.proxy:
            curl.setopt(pycurl.PROXY, '')
        else:
            curl.setopt(pycurl.PROXY, task.request.proxy)
            proxy_type = task.request.proxy_type or 'HTTP'
            proxy_type = getattr(pycurl, 'PROXYTYPE_%s' % proxy_type.upper())
            curl.setopt(pycurl.PROXYTYPE, proxy_type)
            curl.setopt(pycurl.PROXYUSERPWD, task.request.proxy_auth or '')

        # сборщик заголовков
        task.response.header_chunks = []
        curl.setopt(pycurl.HEADERFUNCTION, task.response.header_chunks.append)

        # коллектор тела ответа сервера
        task.response._destination = task.request.body_destination
        curl.setopt(pycurl.WRITEFUNCTION, task.response._writer)

    def process_to_task(self, task, **kwargs):
        '''Возвращает результат выполнения запроса в задачу'''
        #raise NotImplementedError

        # применение параметров из ответа на запрос к таску, чтобы
        # можно было использовать в дальнейшем, например, куки

        curl = kwargs.get('curl', None)

        task.response._process_headers()

        if isinstance(task.response.body, list):
            task.response.body = ''.join(task.response.body)

        task.response.total_time = curl.getinfo(pycurl.TOTAL_TIME)
        task.response.url = curl.getinfo(pycurl.EFFECTIVE_URL)
        task.response.code = curl.getinfo(pycurl.HTTP_CODE)

        cookies = {}
        for line in curl.getinfo(pycurl.INFO_COOKIELIST):
            chunks = line.split('\t')
            cookies[chunks[-2]] = chunks[-1]
        task.response.cookies = cookies

        task.process_response()
