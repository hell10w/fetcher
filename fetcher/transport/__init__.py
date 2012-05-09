# -*- coding: utf-8 -*-

from errors import UnknownFetcherTransport


def get_fetcher_transport(**kwargs):
    '''
    Получение класса транспорта для передачи запросов
    Параметры;
        fetcher_transport - empty/curl
    '''

    transport = kwargs.pop('fetcher_transport', 'curl')

    if transport == 'empty':
        from base_transport import BaseFetcher
        return BaseFetcher

    elif transport == 'curl':
        from curl_transport import CurlFetcher
        return CurlFetcher

    raise UnknownFetcherTransport(u'Неизвестный тип транспорта запросов!')
