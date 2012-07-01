# -*- coding: utf-8 -*-

from time import time


class SpiderStatistics(object):
    def __init__(self):
        pass

    def reset(self):
        self._start_time = time()
        self._end_time = time()

        self.processed_tasks = 0
        self.processed_from_cache = 0
        self.transfer_size = 0
        self.transfer_time = 0

    def hold(self):
        self._end_time = time()

    def show(self):
        print u'Общее время работы: %.2f секунд' % (self._end_time - self._start_time)
        print u'Обработано задач: %d (из кэша: %d)' % (self.processed_tasks, self.processed_from_cache)
        print u'Суммарное время загрузки каждой задачи: %d секунд' % self.transfer_time
        print u'Суммарный объем загруженных данных: %d байт' % self.transfer_size
