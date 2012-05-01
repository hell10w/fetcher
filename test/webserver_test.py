# -*- coding: utf-8 -*-

from unittest import TestCase, main

import requests

from utils.webserver import WebServer


class Test(TestCase):
    options = dict(
        #timeout=0.3,
        #'host': 'localhost'
        port=8080,
        response=dict(
            get='Simple GET-response',
            post='Simple POST-response'
        ),
        cookies={
            'somename': 'somevalue',
            'additional': 'secrettoken'
        }
    )

    def check_request(self, func, url, count=5, check_response={}):
        '''Проверка запросов'''

        responses = [func(url=url) for _ in xrange(count)]

        for response in responses:
            if callable(check_response):
                check_response(response)
            else:
                for key, value in check_response.iteritems():
                    self.assertEquals(getattr(response, key), value)

    def test_get(self):
        '''Проверка GET-запросов'''

        correct_response = dict(
            content=self.options['response']['get'],
            status_code=200
        )

        server = WebServer(**self.options)
        server.start()

        self.check_request(requests.get, server.url, check_response=correct_response)

        server.stop()

    def test_post(self):
        '''Проверка POST-запросов'''

        correct_response = dict(
            content=self.options['response']['post'],
            status_code=200
        )

        server = WebServer(**self.options)
        server.start()

        self.check_request(requests.post, server.url, check_response=correct_response)

        server.stop()

    def test_response_callback(self):
        '''Проверка возможности перенастройки сервера и callback для формирования ответа сервера'''

        ANSWER = '654321'
        REQUEST = lambda: ANSWER

        def response_checker(response):
            self.assertEqual(response.content, ANSWER)

        server = WebServer(**self.options)
        server.start()

        server.setup(
            response=dict(
                get=REQUEST,
                post=REQUEST
            )
        )

        self.check_request(requests.get, server.url, check_response=response_checker)

        server.stop()


if __name__ == "__main__":
    main()
