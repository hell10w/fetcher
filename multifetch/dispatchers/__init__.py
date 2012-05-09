# -*- coding: utf-8 -*-

from errors import UnknownFetcherDispatcher


def get_tasks_manager(**kwargs):
    '''
    Получение экземпляра класса диспетчера задач
    Параметры;
        dispatch_type - empty/curl
    '''

    transport = kwargs.pop('dispatcher_type', 'curl')

    if transport == 'empty':
        from base_dispatch import BaseDispatcher
        return BaseDispatcher(**kwargs)

    elif transport == 'curl':
        from curl_dispatch import CurlDispatcher
        return CurlDispatcher(**kwargs)

    raise UnknownFetcherDispatcher(u'Неизвестный тип диспетчера задач!')
