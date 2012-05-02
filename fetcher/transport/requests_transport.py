# -*- coding: utf-8 -*-

import requests

from empty_transport import BaseFetcher


class RequestsFetcher(BaseFetcher):
    def __init__(self, **kwarg):
        self._options = {}
        self._response = None

        '''
        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param data: (optional) Dictionary or bytes to send in the body of the :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
        :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) Float describing the timeout of the request.
        :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
        :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
        :param return_response: (optional) If False, an un-sent Request object will returned.
        :param session: (optional) A :class:`Session` object to be used for the request.
        :param config: (optional) A configuration dictionary.
        :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        :param prefetch: (optional) if ``True``, the response content will be immediately downloaded.
        '''

    def prepare_from_task(self, task):
        '''Подготавливает запрос из задачи'''

        '''def set_default_from_task(key, value=None):
            self._options.setdefault(key, getattr(task, key, value))

        def set_default(key, value=None):
            self._options.setdefault(key, value)

        #скачивание должно происходить последовательно, а не сразу
        set_default('prefetch', False)
        #
        set_default_from_task('url')
        #
        set_default_from_task('cookies')
        set_default_from_task('allow_redirects')
        set_default('url', None)
        set_default('url', None)
        set_default('url', None)

        self._options.setdefault('url', getattr(task, 'url', None))
        if task.url:
            self._options['url'] = task.url'''

    def process_to_task(self, task):
        '''task.response.status_code = self._response.status_code
        task.response.body = self._response.content'''
        task.process_response()

    def request(self):
        #self._response = requests.get(self._options['url'])
        pass
