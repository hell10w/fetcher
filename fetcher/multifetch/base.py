# -*- coding: utf-8 -*-

from sys import exc_info
from traceback import extract_tb
from logging import getLogger


logger = getLogger('fetcher.multifetcher')


class SpiderBase(object):
    def on_start(self):
        '''Вызывается перед началом работы'''
        pass

    def on_stop(self):
        '''Вызывается по завершении работы'''
        pass

    def on_loop(self):
        '''Вызывается на каждом проходе цикла'''
        pass

    def groups_collector(self, group):
        '''Сюда стекаются все выполненные группы у которых нет обработчиков'''
        yield None

    def tasks_collector(self, task, error=None):
        '''Сюда стекаются все выполненные задачи у которых нет обработчиков'''
        yield None

    def data_collector(self, **kwargs):
        '''Сюда стекаются данные у которых не задан обработчик'''
        yield None

    def _traceback_logger(self):
        exc_type, exc_value, exc_traceback = exc_info()
        traceback = [
            '  File "%s", line %d, in %s\n    %s' % line
            for line in extract_tb(exc_traceback)
        ]
        logger.error(u'Подавление ошибки в обработчике задачи!')
        logger.error('Traceback:\n' + '\n'.join(traceback))
        logger.error(u'%s: %s' % (exc_type.__name__, exc_value))
