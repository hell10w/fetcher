# -*- coding: utf-8 -*-

class BaseFetcher(object):
    def __init__(self, **kwarg):
        pass

    def prepare_from_task(self, task):
        pass

    def process_to_task(self, task):
        pass

    def request(self):
        pass