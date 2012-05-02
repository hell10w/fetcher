# -*- coding: utf-8 -*-

def get_fetcher_transport(**kwargs):
    '''
    Получение класса транспорта для передачи запросов
    Параметры;
        fetcher_transport - empty/requests
    '''

    transport = kwargs.pop('fetcher_transport', 'requests')

    if transport == 'empty':
        from empty_transport import BaseFetcher
        return BaseFetcher

    elif transport == 'requests':
        from requests_transport import RequestsFetcher
        return RequestsFetcher

    raise Exception(u'Неизвестный тип транспорта запросов!')
