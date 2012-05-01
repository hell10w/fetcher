# -*- coding: utf-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import gevent
from gevent.monkey import patch_all, patch_thread


patch_all(thread=False)


class WebServer(gevent.Greenlet):
    '''Простой веб-сервер для тестов'''

    def __init__(self, run=None, *args, **kwargs):
        '''
        Параметры
            host - хост
            port - порт
            response - словарь из ответов на соответствующие запросы
                get - ответ на запрос GET
                post - ответ на запрос POST
            cookies - куки устанавливаемые в ответе
            status_code - код возврата сервера
            timeout - таймаут ответа
        '''

        self.address = (
            kwargs.pop('host', 'localhost'),
            kwargs.pop('port', 80)
            )

        self.url = 'http://%s:%d/' % self.address

        self.httpd = HTTPServer(self.address, get_http_handler(**kwargs))

        super(WebServer, self).__init__(run, *args, **kwargs)

    def _run(self, *args, **kwargs):
        try:
            self.httpd.serve_forever()
        except IOError, exception:
            print exception

    def start(self):
        '''Стартует обработку запросов'''
        super(WebServer, self).start()
        gevent.sleep()

    def stop(self):
        patch_thread()
        self.httpd.shutdown()
        self.httpd.server_close()

    def setup(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self.httpd.RequestHandlerClass, key, value)


def get_http_handler(**kwargs):
    '''Возвращает хэндлер запросов'''

    class HTTPRequestHandler(BaseHTTPRequestHandler):
        '''Класс-хэндлер запросов'''

        def do_GET(self):
            '''Вызывается при GET-запросе'''
            self.do_answer(self.response['get'])

        def do_POST(self):
            '''Вызывается при POST-запросе'''
            self.do_answer(self.response['post'])

        def log_message(*args, **kwargs):
            '''Ничего не логгируется'''
            pass

        def do_answer(self, response_body=None):
            '''Унифицированный метод ответа на запрос'''

            # таймаут
            if self.timeout:
                gevent.sleep(self.timeout)

            # формирование заголовка
            self.send_response(self.status_code)
            for key, value in self.cookies.iteritems():
                self.send_header('Set-Cookie', '%s=%s' % (key, value))
            self.end_headers()

            # тело ответа
            if response_body:
                if callable(response_body):
                    response_body = response_body()
                self.wfile.write(response_body)

    Class = HTTPRequestHandler

    # заполенение параметров
    Class.timeout = kwargs.pop('timeout', None)
    Class.response = kwargs.pop(
        'response',
            {
            'get': '',
            'post': ''
        }
    )
    Class.status_code = kwargs.pop('status_code', 200)
    Class.cookies = kwargs.pop('cookies', {})

    return Class
