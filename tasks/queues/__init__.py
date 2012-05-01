# -*- coding: utf-8 -*-

def get_tasks_queue(**kwargs):
    '''
    Получение экземпляра класса очереди задач в зависиости от её размещения
    Параметры;
        queue_transport - вид размещения очереди
            (в памяти - memory, или в mongo - mongo)
    '''

    transport = kwargs.pop('queue_transport', 'mongo')

    if transport == 'memory':
        from memory_queue import MemoryQueue
        return MemoryQueue(**kwargs)

    if transport == 'mongo':
        from mongo_queue import MongoQueue
        return MongoQueue(**kwargs)

    raise Exception(u'Неизвестный тип очереди!')
