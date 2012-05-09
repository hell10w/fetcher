# -*- coding: utf-8 -*-

import pycurl

from base_transport import BaseFetcher
from fetcher.temporaryfile import TempFile
from fetcher.useragents import get_user_agent


class CurlFetcher(BaseFetcher):
    '''Транспорт для запросов на библиотеке Curl'''

    def __init__(self, **kwarg):
        super(CurlFetcher, self).__init__()

        self.curl = kwarg.pop('curl', None)

        if not self.curl:
            self.curl = pycurl.Curl()

        #self.curl.fetcher = self

    #def __del__(self):
    #    CurlFetcher.curls_pool.append(self.curl)

    def prepare_from_task(self, task):
        '''Подготавливает запрос из задачи'''

        '''
            *method = 'GET'
            *url = None
            *additional_headers = {}
            cookies = {}
            body = None

            *allow_redirects = True
            *max_redirects = 3
        '''

        self.curl.task = task
        self.curl.fetcher = self

        self.curl.setopt(pycurl.URL, task.request.url)
        self.curl.setopt(pycurl.HTTPGET, 1)
        self.curl.setopt(pycurl.WRITEFUNCTION, lambda chunk: None)

        return

        self.curl.setopt(pycurl.URL, task.request.url)

        follow_location = 0
        if task.request.allow_redirects:
            follow_location = 1
        self.curl.setopt(pycurl.FOLLOWLOCATION, follow_location)
        self.curl.setopt(pycurl.MAXREDIRS, task.request.max_redirects)

        self.curl.setopt(pycurl.CONNECTTIMEOUT, task.request.connection_timeout or 0)
        self.curl.setopt(pycurl.TIMEOUT, task.request.timeout or 0)

        self.curl.setopt(pycurl.NOSIGNAL, 1) # TODO: что это?
        self.curl.setopt(pycurl.WRITEFUNCTION, self.write_function) # TODO: нет этой функции
        #self.curl.setopt(pycurl.HEADERFUNCTION, self.head_processor) # TODO: нет этой функции
        self.curl.setopt(pycurl.WRITEFUNCTION, lambda: None) # TODO: нет этой функции

        self.curl.setopt(pycurl.USERAGENT, task.request.user_agent or '')

        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        self.curl.setopt(pycurl.VERBOSE, 0)
        self.curl.setopt(pycurl.DEBUGFUNCTION, lambda: None)

        if task.request.method == 'GET':
            self.curl.setopt(pycurl.HTTPGET, 1)
        elif task.request.method == 'POST':
            raise NotImplementedError
            # TODO: POST
            raise NotImplementedError
            '''if not task.request.body:
                self.curl.setopt(pycurl.POSTFIELDS, '')
            else:
                if type(task.request.body) == TempFile:
                    self.curl.setopt(
                        pycurl.READFUNCTION,
                        task.request.body.read
                    )
                elif type(task.request.body) == file:
                    self.curl.setopt(
                        pycurl.READFUNCTION,
                        task.request.body.read
                    )
                else:
                    self.curl.setopt(
                        pycurl.READFUNCTION,
                        StringIO(task.request.body).read
                    )'''
        elif task.request.method == 'PUT':
            # TODO: PUT
            #self.curl.setopt(pycurl.READFUNCTION, StringIO(grab.config['post']).read)
            raise NotImplementedError
        elif task.request.method == 'DELETE':
            self.curl.setopt(pycurl.CUSTOMREQUEST, 'delete')
        elif task.request.method == 'HEAD':
            self.curl.setopt(pycurl.NOBODY, 1)
        elif task.request.method == 'UPLOAD':
            self.curl.setopt(pycurl.UPLOAD, 1)
        else:
            raise NotImplementedError

        headers = [
            '%s: %s' % x
            for x in task.request.additional_headers.iteritems()
        ]
        self.curl.setopt(pycurl.HTTPHEADER, headers)

        if 'zlib' in pycurl.version:
            self.curl.setopt(pycurl.ENCODING, 'gzip')

        # TODO: COOKIE !!!!!!!!!!!!!!!!
        # TODO: BODY   !!!!!!!!!!!!!!!!
        # TODO: PROXY  !!!!!!!!!!!!!!!!

        return

        ###########################

        if grab.request_method == 'POST':
            self.curl.setopt(pycurl.POST, 1)
            if grab.config['multipart_post']:
                if isinstance(grab.config['multipart_post'], basestring):
                    raise error.GrabMisuseError('multipart_post option could not be a string')
                post_items = normalize_http_values(grab.config['multipart_post'],
                                                   charset=grab.config['charset'])
                self.curl.setopt(pycurl.HTTPPOST, post_items)
            elif grab.config['post']:
                if isinstance(grab.config['post'], basestring):
                    # bytes-string should be posted as-is
                    # unicode should be converted into byte-string
                    if isinstance(grab.config['post'], unicode):
                        post_data = normalize_unicode(grab.config['post'])
                    else:
                        post_data = grab.config['post']
                else:
                    # dict, tuple, list should be serialized into byte-string
                    post_data = urlencode(grab.config['post'])
                self.curl.setopt(pycurl.POSTFIELDS, post_data)
            else:
                self.curl.setopt(pycurl.POSTFIELDS, '')
        elif grab.request_method == 'PUT':
            self.curl.setopt(pycurl.PUT, 1)

        if grab.config['cookiefile']:
            grab.load_cookies(grab.config['cookiefile'])

        if grab.config['cookies']:
            if not isinstance(grab.config['cookies'], dict):
                raise error.GrabMisuseError('cookies option shuld be a dict')
            items = encode_cookies(grab.config['cookies'], join=False)
            self.curl.setopt(pycurl.COOKIELIST, 'ALL')
            for item in items:
                self.curl.setopt(pycurl.COOKIELIST, 'Set-Cookie: %s' % item)
        else:
            # Turn on cookies engine anyway
            # To correctly support cookies in 302-redirects
            self.curl.setopt(pycurl.COOKIEFILE, '')

        if grab.config['referer']:
            self.curl.setopt(pycurl.REFERER, str(grab.config['referer']))

        if grab.config['proxy']:
            self.curl.setopt(pycurl.PROXY, str(grab.config['proxy']))
        else:
            self.curl.setopt(pycurl.PROXY, '')

        if grab.config['proxy_userpwd']:
            self.curl.setopt(pycurl.PROXYUSERPWD, grab.config['proxy_userpwd'])

        # PROXYTYPE
        # Pass a long with this option to set type of the proxy. Available options for this are CURLPROXY_HTTP, CURLPROXY_HTTP_1_0 (added in 7.19.4), CURLPROXY_SOCKS4 (added in 7.15.2), CURLPROXY_SOCKS5, CURLPROXY_SOCKS4A (added in 7.18.0) and CURLPROXY_SOCKS5_HOSTNAME (added in 7.18.0). The HTTP type is default. (Added in 7.10)

        if grab.config['proxy_type']:
            ptype = getattr(pycurl, 'PROXYTYPE_%s' % grab.config['proxy_type'].upper())
            self.curl.setopt(pycurl.PROXYTYPE, ptype)

        if grab.config['encoding']:
            if 'gzip' in grab.config['encoding'] and not 'zlib' in pycurl.version:
                raise error.GrabMisuseError('You can not use gzip encoding because '\
                                            'pycurl was built without zlib support')
            self.curl.setopt(pycurl.ENCODING, grab.config['encoding'])

        if grab.config['userpwd']:
            self.curl.setopt(pycurl.USERPWD, grab.config['userpwd'])

        raise NotImplementedError

    def process_to_task(self, task):
        '''Возвращает результат выполнения запроса в задачу'''
        #raise NotImplementedError

        # применение параметров из ответа на запрос к таску, чтобы
        # можно было использовать в дальнейшем, например, куки
        task.process_response()

    def request(self):
        '''Выполняет запрос'''
        #raise NotImplementedError

    def write_function(self, chunk):
        print chunk
        return None
