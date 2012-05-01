# -*- coding: utf-8 -*-

class Response(object):
    def __init__(self, **kwargs):
        self.status_code = kwargs.pop('status_code', None)
        self.body = kwargs.pop('body', None)
        self.cookies = kwargs.pop('cookies', {})
