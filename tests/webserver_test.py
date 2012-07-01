# -*- coding: utf-8 -*-

from unittest import TestCase, main

import requests

from tests.utils import WebServer, ServerOptions


class Test(TestCase):
    def setUp(self):
        WebServer().start()

    def test_get(self):
        '''Проверка GET-запросов тестового сервера'''

        ServerOptions.RESPONSE['GET'] = 'checking get method'

        response = requests.get(ServerOptions.SERVER_URL)

        self.assertEquals(response.content, ServerOptions.RESPONSE['GET'])

    def test_post(self):
        '''Проверка POST-запросов тестового сервера'''

        DATA = 'checking post method'
        ServerOptions.RESPONSE['POST'] = lambda: ServerOptions.REQUEST['POST']

        response = requests.post(ServerOptions.SERVER_URL, DATA)

        self.assertEquals(response.content, DATA)


if __name__ == "__main__":
    main()
