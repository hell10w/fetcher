# -*- coding: utf-8 -*-

class BaseFetcher(object):
    '''Базов класс транспорта запросов'''

    # варианты поведения сервера для сохранения
    # ответа сервера
    AUTO_RESPONSE_BODY = 0 # автоматически определять
    MEMORY_RESPONSE_BODY = 1 # сохранять в память всегда
    FILE_RESPONSE_BODY = 2 # сохранять в файл всегда
    # поведение транспорта по сохранению ответа сервера
    response_body_destination = AUTO_RESPONSE_BODY

    # максимальный размер при котором скачивание
    # ответа сервера происходит в память
    file_cache_size = 10 * 1024
    # размер буфера для перекачивания из сокета в файл
    body_download_chunk = 10 * 1024

    def __init__(self, **kwarg):
        pass

    def prepare_from_task(self, task):
        '''Метод должен преобразовывать таск в структуры транспорта'''
        raise NotImplementedError

    def process_to_task(self, task):
        '''Метод должен выполнять обратное преобразование структур транспорта в таск'''
        raise NotImplementedError

    def request(self):
        '''Метод должен выполнять запрос'''
        raise NotImplementedError