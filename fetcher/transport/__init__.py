# -*- coding: utf-8 -*-

def get_fetcher_transport(**kwargs):
    '''
    Получение класса транспорта для передачи запросов
    Параметры;
        fetcher_transport - empty/requests/curl
    '''

    transport = kwargs.pop('fetcher_transport', 'curl')

    if transport == 'empty':
        from empty_transport import BaseFetcher
        return BaseFetcher

    elif transport == 'requests':
        from requests_transport import RequestsFetcher
        return RequestsFetcher

    elif transport == 'curl':
        from curl_transport import CurlFetcher
        return CurlFetcher

    raise Exception(u'Неизвестный тип транспорта запросов!')
