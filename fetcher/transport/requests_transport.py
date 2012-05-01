# -*- coding: utf-8 -*-

import requests

from empty_transport import BaseFetcher


class RequestsFetcher(BaseFetcher):
    def __init__(self, **kwarg):
        self._options = {
            'url': 'http://google.ru/'
        }
        self._response = None

    def prepare_from_task(self, task):
        if task.url:
            self._options['url'] = task.url

    def process_to_task(self, task):
        task.response.status_code = self._response.status_code
        task.response.body = self._response.content
        task.process_response()

    def request(self):
        self._response = requests.get(self._options['url'])


Fetcher = RequestsFetcher