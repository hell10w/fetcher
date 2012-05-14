# -*- coding: utf-8 -*-


class BaseFetcher(object):
    '''Базов класс транспорта запросов'''

    def __init__(self, **kwarg):
        pass

    def prepare_from_task(self, task, **kwargs):
        '''Метод должен преобразовывать таск в структуры транспорта'''
        raise NotImplementedError

    def process_to_task(self, task, **kwargs):
        '''Метод должен выполнять обратное преобразование структур транспорта в таск'''
        raise NotImplementedError
