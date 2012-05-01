# -*- coding: utf-8 -*-

def get_tasks_manager(**kwargs):
    '''
    Получение экземпляра класса диспетчера задач
    Параметры;
        dispatch_type - empty/gevent
    '''

    transport = kwargs.pop('dispatcher_type', 'gevent')

    if transport == 'empty':
        from empty_dispatch import BaseDispatcher
        return BaseDispatcher(**kwargs)

    elif transport == 'gevent':
        from gevent_dispatch import GreenletDispatcher
        return GreenletDispatcher(**kwargs)

    raise Exception(u'Неизвестный тип диспетчера задач!')
