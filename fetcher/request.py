# -*- coding: utf-8 -*-

from fetcher.useragents import get_user_agent


MEMORY_RESPONSE_BODY = 0    # сохранять ответа сервера в память
FILE_RESPONSE_BODY = 1      # сохранять ответа сервера в файл


class Request(object):
    '''Запроса серверу'''

    method = 'GET'
    url = None
    additional_headers = {}
    user_agent = get_user_agent()
    referer = None
    cookies = {}
    post = None

    allow_redirects = True
    max_redirects = 3

    proxy = None
    proxy_type = 'HTTP' # HTTP / SOCKS4 / SOCKS5
    proxy_auth = None # username:password

    connection_timeout = None
    overall_timeout = None

    # поведение транспорта по сохранению ответа сервера
    body_destination = MEMORY_RESPONSE_BODY

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)