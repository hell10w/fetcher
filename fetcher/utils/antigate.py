# -*- coding: utf-8 -*-

from fetcher.tasks import Task
from fetcher.fetch.extensions import PostFile


class Antigate(object):
    @classmethod
    def send(cls, handler=None, key=None, filename=None,
             phrase=False, regsense=False, numeric=False,
             min_len=0, max_len=30):
        if not key:
            raise Exception(u'Ключ для Antigate должен быть указан!')

        if not filename:
            raise Exception(u'Не указан файл капчи!')

        if not handler:
            raise Exception(u'Обработчик задачи должен быть указан!')

        params = dict(
            key=key,
            filename=filename
        )

        post = [
            ('method', 'post'),
            ('phrase', '1' if phrase else '0'),
            ('regsense', '1' if regsense else '0'),
            ('numeric', '1' if numeric else '0'),
            ('min_len', str(min_len)),
            ('max_len', str(max_len)),
            ('key', params['key']),
            ('file', PostFile(filename=params['filename']))
        ]

        return Task(
            url='http://antigate.com/in.php',
            method='POST',
            is_multipart_post=True,
            post=post,
            internal_data=params,
            handler=handler
        )

    @classmethod
    def send_handler(cls, task, error=None, handler=None):
        if not handler:
            raise Exception(u'Обработчик задачи должен быть указан!')
        if error or task.response.status_code != 200:
            return
        try:
            captcha_id = int(task.response.content.split('|')[1])
            return Task(
                url='http://antigate.com/res.php',
                post=[
                    ('key', task.internal_data['key']),
                    ('action', 'get'),
                    ('id', captcha_id)
                ],
                handler=handler
            )
        except:
            pass

    @classmethod
    def state_handler(cls, task, error=None):
        result, error_message = False, None

        if not error and task.response.status_code == 200:
            content = task.response.content

            if content != 'CAPCHA_NOT_READY':
                content = content.split('|')
                logger.info('capres: %s' % content)
                if len(content) == 2:
                    result = content[1]
                else:
                    error_message = content[0]

        return (result, error_message)
