# -*- coding: utf-8 -*-

def get_tasks_manager(**kwargs):
    '''
    Получение экземпляра класса диспетчера задач
    Параметры;
        dispatch_type - empty/gevent/curl
    '''

    transport = kwargs.pop('dispatcher_type', 'curl')

    if transport == 'empty':
        from empty_dispatch import BaseDispatcher
        return BaseDispatcher(**kwargs)

    elif transport == 'gevent':
        from gevent_dispatch import GreenletDispatcher
        return GreenletDispatcher(**kwargs)

    elif transport == 'curl':
        from curl_dispatch import CurlDispatcher
        return CurlDispatcher(**kwargs)

    raise Exception(u'Неизвестный тип диспетчера задач!')
