# -*- coding: utf-8 -*-

import pycurl

from fetcher.fetch import Fetcher
from fetcher.multifetch.dispatcher.base import BaseDispatcher
from fetcher.errors import TimeoutError, ConnectionError, AuthError, NetworkError


class CurlDispatcher(BaseDispatcher):
    '''Менеджер задач на основе CurlMulti'''

    def __init__(self, **kwargs):
        super(CurlDispatcher, self).__init__()

        self.threads_count = kwargs.pop('threads_count', 20)

        self.fetcher = Fetcher()

        self.multi_handle = pycurl.CurlMulti()
        self.multi_handle.handles = [
            pycurl.Curl()
            for _ in xrange(self.threads_count)
        ]
        self.curls_pool = self.multi_handle.handles[:]

    def __del__(self):
        for curl in self.multi_handle.handles:
            curl.close()
        self.multi_handle.close()

    def process_task(self, task):
        '''Стартует асинхронное выполнение задачи'''
        curl = self.curls_pool.pop()

        self.fetcher.prepare_from_task(task, curl=curl)
        curl.task = task

        self.multi_handle.add_handle(curl)

    def is_empty(self):
        '''Проверяет пустоту пула выполняемых задач'''
        return len(self.curls_pool) == self.threads_count

    def is_full(self):
        '''Проверяет заполненность пула выполняемых задач'''
        return not len(self.curls_pool)

    def wait_available(self):
        '''Проверяет выполненность задач в пуле'''
        while True:
            status, active_objects = self.multi_handle.perform()
            if status != pycurl.E_CALL_MULTI_PERFORM:
                break

    def finished_tasks(self):
        '''Генератор выполненных задач'''
        while True:
            # извлечение информации о выполненных и сбойнувших Curl объектах
            queue_size, success_list, failed_list = self.multi_handle.info_read()
            # обработка выполненных Curl объектов
            for curl in success_list:
                yield  self.process_finished_curl(curl), None
            # обработка сбойнувших Curl объектов
            for curl, error_code, error_message in failed_list:
                error = None
                if error_code == pycurl.E_WRITE_ERROR:
                    pass
                elif error_code == pycurl.E_OPERATION_TIMEOUTED:
                    error = TimeoutError(error_code, error_message)
                elif error_code == pycurl.E_COULDNT_CONNECT:
                    error = ConnectionError(error_code, error_message)
                elif error_code == pycurl.E_LOGIN_DENIED:
                    error = AuthError(error_code, error_message)
                else:
                    error = NetworkError(error_code, error_message)
                yield self.process_failed_curl(curl), error
            #
            if queue_size == 0:
                break
        self.multi_handle.select(0.1)

    def process_finished_curl(self, curl):
        '''Обрабатывает таск из выполненного Curl объекта'''
        task = curl.task
        self.fetcher.process_to_task(task, curl=curl)
        curl.task = None
        self.multi_handle.remove_handle(curl)
        self.curls_pool.append(curl)
        return task

    def process_failed_curl(self, curl):
        '''Возвращает таск из сбойнувшего Curl объекта'''
        task = curl.task
        curl.task = None
        self.multi_handle.remove_handle(curl)
        self.curls_pool.append(curl)
        return task
