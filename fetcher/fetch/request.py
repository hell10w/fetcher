# -*- coding: utf-8 -*-

from fetcher.fetch.useragents import get_user_agent


MEMORY_RESPONSE_BODY = 0    # сохранять ответ сервера в память
FILE_RESPONSE_BODY = 1      # сохранять ответ сервера в файл
AUTO_RESPONSE_BODY = 2      # автоматически определять


class Request(object):
    '''Запроса серверу'''

    def __init__(self, **kwargs):
        # основные настройки запроса
        self.method = 'GET'
        self.url = None
        self.additional_headers = {
            'Accept-Language': 'en-us,en;q=0.9',
            'Accept-Charset': 'utf-8',
            'Keep-Alive': '300',
            'Expect': '',
        }
        self.user_agent = get_user_agent()
        self.referer = None
        self.cookies = {}
        self.post = None
        self.is_multipart_post = False

        self.allow_redirects = True
        self.max_redirects = 3

        self.proxy = None
        self.proxy_type = 'HTTP' # HTTP / SOCKS4 / SOCKS5
        self.proxy_auth = None # username:password

        self.connection_timeout = None
        self.overall_timeout = None

        # поведение транспорта по сохранению ответа сервера
        self.body_destination = AUTO_RESPONSE_BODY
        self.container_options = None

        self.setup(**kwargs)

    def setup(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        return self

    def clone(self, **kwargs):
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key[0] == '_'
        )
        return Request(**_kwargs).setup(**kwargs)
