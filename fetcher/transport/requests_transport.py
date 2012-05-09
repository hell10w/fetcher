# -*- coding: utf-8 -*-

import requests

from empty_transport import BaseFetcher
from fetcher.response import TempFile


class RequestsFetcher(BaseFetcher):
    '''Транспорт для запросов на библиотеке requests'''

    session = requests.session()

    default_options = dict(
        prefetch=False,
        method='GET',
        headers={
            'Accept-Charset': 'utf-8'
        }
    )

    def __init__(self, **kwarg):
        super(RequestsFetcher, self).__init__()
        self._options = self.default_options

    def prepare_from_task(self, task):
        '''Подготавливает запрос из задачи'''

        '''
           - :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
           ! :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
           ! :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
           - :param return_response: (optional) If False, an un-sent Request object will returned.
           - :param session: (optional) A :class:`Session` object to be used for the request.
           ? :param config: (optional) A configuration dictionary.
           ! :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        '''

        # TODO: генерация ошибок:
        # 1. нет URL
        # 2. нет method

        overload_config = {}
        overload_config['method'] = task.request.method
        overload_config['url'] = task.request.url
        overload_config['cookies'] = task.request.cookies
        overload_config['headers'] = {'User-Agent': task.request.user_agent}
        overload_config['headers'].update(task.request.additional_headers)

        overload_config['allow_redirects'] = task.request.allow_redirects
        # TODO: может это не глобальный конфиг
        overload_config['config'] = {'max_redirects': task.request.max_redirects}
        # TODO: может можно проверить task.request.proxies и вообще не устанавливать
        overload_config['proxies'] = task.request.proxies
        overload_config['data'] = task.request.body # сработает и для post-запроса
        # TODO: будет ли работать на None и что-то другое устанавливать по-умолчанию
        overload_config['timeout'] = task.request.timeout
        # TODO: проверка сертификата
        #overload_config['verify'] = ???
        # TODO: отправка файлов с помощью самого requests
        #overload_config['files'] = ???
        # TODO: аутентификация
        #overload_config['auth'] = ???

        self._options.update(overload_config)

    def process_to_task(self, task):
        '''Возвращает результат выполнения запроса в задачу'''

        # сохранение основных параметров ответа
        task.response.status_code = self._response.status_code
        task.response.url = self._response.url
        task.response.cookies = self._response.cookies
        task.response.headers = self._response.headers

        # кодировка документа
        task.response.encoding = self._response.encoding

        # опредедение места сохранения ответа сервера
        destination = self.MEMORY_RESPONSE_BODY

        if self.response_body_destination == self.AUTO_RESPONSE_BODY:
            content_length = int(self._response.headers.get('Content-Length', 0))
            if content_length > self.file_cache_size:
                destination = self.FILE_RESPONSE_BODY
            else:
                destination = self.MEMORY_RESPONSE_BODY
        elif self.response_body_destination == self.FILE_RESPONSE_BODY:
            destination = self.FILE_RESPONSE_BODY
        elif self.response_body_destination == self.MEMORY_RESPONSE_BODY:
            destination = self.MEMORY_RESPONSE_BODY

        # сохранение ответа сервера
        if destination == self.FILE_RESPONSE_BODY:
            task.response.body = TempFile()
            data_iterator = self._response.iter_content(
                chunk_size=RequestsFetcher.body_download_chunk,
                decode_unicode=True
            )
            for block in data_iterator:
                task.response.body.write(block)
        elif destination == self.MEMORY_RESPONSE_BODY:
            task.response.body = self._response.content

        # применение параметров из ответа на запрос к таску, чтобы
        # можно было использовать в дальнейшем, например, куки
        task.process_response()

    def request(self):
        '''Выполняет запрос'''

        self._response = RequestsFetcher.session.request(
            method=self._options.pop('method'),
            url=self._options.pop('url'),
            **self._options
        )
