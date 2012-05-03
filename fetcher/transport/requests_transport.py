# -*- coding: utf-8 -*-

import requests

from empty_transport import BaseFetcher
from fetcher.response import TempFile
from fetcher.useragents import get_user_agent


class RequestsFetcher(BaseFetcher):
    session = requests.session()

    default_options = dict(
        prefetch=False,
        method='GET',
        headers={
            'User-Agent': get_user_agent(),
            'Accept-Charset': 'utf-8'
        }
    )

    def __init__(self, **kwarg):
        super(RequestsFetcher, self).__init__()
        self._options = self.default_options

    def prepare_from_task(self, task):
        '''Подготавливает запрос из задачи'''

        '''
            :param method: method for the new :class:`Request` object.
           * :param url: URL for the new :class:`Request` object.
           - :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
           * :param data: (optional) Dictionary or bytes to send in the body of the :class:`Request`.
           * :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
           * :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
           ! :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
           ! :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
           * :param timeout: (optional) Float describing the timeout of the request.
           * :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
           * :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
           - :param return_response: (optional) If False, an un-sent Request object will returned.
           - :param session: (optional) A :class:`Session` object to be used for the request.
           ? :param config: (optional) A configuration dictionary.
           ! :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
           * :param prefetch: (optional) if ``True``, the response content will be immediately downloaded.
        '''

        # TODO: генерация ошибок:
        # 1. нет URL
        # 2. нет method

        overload_config = {}
        overload_config['method'] = task.request.method
        overload_config['url'] = task.request.url
        overload_config['cookies'] = task.request.cookies
        overload_config['headers'] = task.request.additional_headers
        overload_config['allow_redirects'] = task.request.allow_redirects
        # TODO: может это не глобальный конфиг
        overload_config['config'] = {'max_redirects': task.request.max_redirects}
        # TODO: может можно проверить task.request.proxies и вообще не устанавливать
        overload_config['proxies'] = task.request.proxies
        overload_config['data'] = task.request.body # сработает и для post-запроса
        # TODO: будет ли работать на None и что-то другое устанавливать по-умолчанию
        overload_config['timeout'] = task.request.timeout
        # TODO: проверка сертификата
        #overload_config['verify'] = ???
        # TODO: отправка файлов не через body
        #overload_config['files'] = ???
        # TODO: аутентификация
        #overload_config['auth'] = ???

        self._options.update(overload_config)

    def process_to_task(self, task):
        '''Возвращает результат выполнения запроса в задачу'''

        task.response.status_code = self._response.status_code
        task.response.url = self._response.url
        task.response.cookies = self._response.cookies
        task.response.headers = self._response.headers

        task.response.body = TempFile()
        with open(task.response.body.name, 'wb') as dump:
            for block in self._response.iter_content():
                dump.write(block)

        '''
           -config      Dictionary of configurations for this request.
           -content     Content of the response, in bytes.
           *cookies     A CookieJar of Cookies the server sent back.
            encoding    Encoding to decode with when accessing r.content.
            error       Resulting HTTPError of request, if one occurred.
           *headers     Case-insensitive Dictionary of Response Headers. For example, headers['content-encoding'] will return the value of a 'Content-Encoding' response header.
           -history     A list of Response objects from the history of the Request. Any redirect responses will end up here.
            iter_content Iterates over the response data. This avoids reading the content at once into memory for large responses. The chunk size is the number of bytes it should read into memory. This is not necessarily the length of each item returned as decoding can take place.
            iter_lines  Iterates over the response data, one line at a time. This avoids reading the content at once into memory for large responses.
            raise_for_status Raises stored HTTPError or URLError, if one occurred.
            raw         File-like object representation of response (for advanced usage).
           -request     The Request that created the Response.
           *status_code Integer Code of responded HTTP Status.
           -text        Content of the response, in unicode. if Response.encoding is None and chardet module is available, encoding will be guessed.
           *url         Final URL location of Response.
        '''

        task.process_response()

    def request(self):
        '''Выполняет запроса'''
        
        self._response = RequestsFetcher.session.request(
            method=self._options.pop('method'),
            url=self._options.pop('url'),
            **self._options
        )
