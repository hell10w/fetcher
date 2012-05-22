# -*- coding: utf-8 -*-

from fetcher.fetch.useragents import get_user_agent


MEMORY_RESPONSE_BODY = 0    # сохранять ответ сервера в память
FILE_RESPONSE_BODY = 1      # сохранять ответ сервера в файл
AUTO_RESPONSE_BODY = 2      # автоматически определять


class Request(object):
    '''Запроса серверу'''

    method = 'GET'
    url = None
    additional_headers = {
        'Accept-Language': 'en-us,en;q=0.9',
        'Accept-Charset': 'utf-8',
        'Keep-Alive': '300',
        'Expect': '',
    }
    user_agent = get_user_agent()
    referer = None
    cookies = {}
    post = None
    is_multipart_post = False

    allow_redirects = True
    max_redirects = 3

    proxy = None
    proxy_type = 'HTTP' # HTTP / SOCKS4 / SOCKS5
    proxy_auth = None # username:password

    connection_timeout = None
    overall_timeout = None

    # поведение транспорта по сохранению ответа сервера
    body_destination = FILE_RESPONSE_BODY

    temp_file_options = None

    def __init__(self, **kwargs):
        self.setup(**kwargs)

    def setup(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        return self

    def clone(self, **kwargs):
        _kwargs = dict(
            (key, value)
            for key, value in self.__dict__.iteritems()
            if not key.startswith('_')
        )
        return Request(**_kwargs).setup(**kwargs)
