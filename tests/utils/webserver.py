# -*- coding: utf-8 -*-

from time import sleep
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class ServerOptions:
    SERVER_URL = None

    TIMEOUT = None

    RESPONSE = None
    STATUS_CODE = None
    COOKIES = None

    REQUEST = None

    @classmethod
    def clean_up(cls):
        ServerOptions.SERVER_URL = None

        ServerOptions.TIMEOUT = None
        ServerOptions.RESPONSE = {
            'GET': '',
            'POST': ''
        }
        ServerOptions.STATUS_CODE = 200
        ServerOptions.COOKIES = {}

        ServerOptions.REQUEST = {
            'PATH': '',
            'HEADERS': [],
            'POST': ''
        }


class HTTPRequestHandler(BaseHTTPRequestHandler):
    '''Класс-хэндлер запросов'''

    def do_GET(self):
        '''Вызывается при GET-запросе'''
        self.do_answer(ServerOptions.RESPONSE['GET'])

    def do_POST(self):
        '''Вызывается при POST-запросе'''
        self.do_answer(ServerOptions.RESPONSE['POST'])

    def log_message(*args, **kwargs):
        '''Ничего не логгируется'''
        pass

    def do_answer(self, response_body=None):
        '''Унифицированный метод ответа на запрос'''

        # таймаут
        if ServerOptions.TIMEOUT:
            sleep(ServerOptions.TIMEOUT)

        content_length = self.headers.getheader('content-length')
        if content_length:
            ServerOptions.REQUEST['POST'] = self.rfile.read(int(content_length))
        ServerOptions.REQUEST['HEADERS'] = self.headers
        ServerOptions.REQUEST['PATH'] = self.path

        # формирование заголовка
        self.send_response(ServerOptions.STATUS_CODE)
        for key, value in ServerOptions.COOKIES.iteritems():
            self.send_header('Set-Cookie', '%s=%s' % (key, value))
        self.end_headers()

        # тело ответа
        if response_body:
            if callable(response_body):
                response_body = response_body()
            self.wfile.write(response_body)


class WebServer(Thread):
    '''Простой веб-сервер для тестов'''

    def __init__(self, host='localhost', port=8080, *args, **kwargs):
        super(WebServer, self).__init__(*args, **kwargs)
        self.daemon = True
        self.address = (host, port)

    def start(self):
        super(WebServer, self).start()
        sleep(0.1)

    def run(self):
        ServerOptions.clean_up()
        ServerOptions.SERVER_URL = 'http://%s:%d/' % self.address
        try:
            httpd = HTTPServer(self.address, HTTPRequestHandler)
            httpd.serve_forever()
        except IOError:
            pass
