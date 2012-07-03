# -*- coding: utf-8 -*-

from logging import getLogger

from fetcher.tasks import Task, ProcessItem
from fetcher.fetch.extensions import PostFile


logger = getLogger('fetcher.antigate')


class Antigate(object):
    '''API для работы с antigate.com'''

    @classmethod
    def recognize(cls, key=None, filename=None,
                       phrase=0, regsense=0,
                       numeric=0, calc=0,
                       is_russian=0,
                       min_len=0, max_len=0,
                       handler=None,
                       extra_data=None):
        '''
            Отправка капчи на разгадывание

            key - ключ к антигейту
            filename - имя файла с капчей
            data_handler - имя обработчика данных который получит ответ на капчу
            extra_data - дополнительные пользовательские данные

            Параметры для антигейта:
            phrase => 0 или 1
                (0 по умолчанию, 1 помечает что у капчи 2-4 слова)
            regsense => 0 или 1
                (0 по умолчанию, 1 помечает что текст капчи чувствителен к регистру) не работает?
            numeric => 0 или 1 или 2
                (0 по умолчанию, 1 помечает что текст капчи состоит только из цифр, 2 помечает что на капче нет цифр)
            calc => 0 или 1
                (0 по умолчанию, 1 помечает что цифры на капче должны быть сплюсованы)
            min_len => 0..20
                (0 по-умолчанию, помечает минимальную длину текста капчи)
            max_len => 0..20
                (0 - без ограничений, помечает максимальную длину капчи)
            is_russian => 0 или 1 или 2
                (0 по умолчанию, 1 помечает что вводить нужно только русский текст, 2 - русский или английский)
        '''

        if not key:
            raise Exception(u'Ключ для Antigate должен быть указан!')

        if not filename:
            raise Exception(u'Не указан файл капчи!')

        if not handler:
            raise Exception(u'Обработчик капчи должен быть указан!')

        internal_data = dict(
            key=key,
            filename=filename,
            extra_data=extra_data,
            handler=ProcessItem(handler=handler)
        )

        post = [
            ('method', 'post'),
            ('phrase', str(phrase)),
            ('regsense', str(regsense)),
            ('numeric', str(numeric)),
            ('min_len', str(min_len)),
            ('max_len', str(max_len)),
            ('calc', str(calc)),
            ('is_russian', str(is_russian)),
            ('key', key),
            ('file', PostFile(filename=filename))
        ]

        return Task(
            url='http://antigate.com/in.php',
            method='POST',
            is_multipart_post=True,
            post=post,
            internal_data=internal_data,
            priority=1,
            no_cache_store=True,
            no_cache_restore=True,
            handler=cls._send_result
        )

    @classmethod
    def _send_result(cls, task, error=None):
        if error or task.response.status_code != 200:
            logger.error(u'Ошибка при отправке капчи!')
            yield task
            return

        try:
            captcha_id = int(task.response.content.split('|')[1])
            logger.info(u'Капча отправлена - id %d!' % captcha_id)

            task.internal_data['captcha_id'] = captcha_id

            yield Task(
                url='http://antigate.com/res.php',
                post=[
                    ('key', task.internal_data['key']),
                    ('action', 'get'),
                    ('id', captcha_id)
                ],
                internal_data=task.internal_data,
                priority=1,
                no_cache_store=True,
                no_cache_restore=True,
                handler=cls._status
            )

        except Exception:
            pass

    @classmethod
    def _status(cls, task, error=None):
        if error or task.response.status_code != 200:
            yield task
            return

        content = task.response.content

        if content == 'CAPCHA_NOT_READY':
            logger.info(u'Капча %d не готова!' % task.internal_data['captcha_id'])
            yield task
            return

        captcha, error = None, None

        content = content.split('|')
        if len(content) == 2:
            captcha = content[1]
        else:
            error = content[0]

        logger.info(u'Результат разгадывания капчи: %s/%s' % (captcha, error))

        handler = task.internal_data.pop('handler')
        handler.update(
            captcha=captcha,
            error=error,
            data=task.internal_data,
            no_cache_store=True,
            no_cache_restore=True,
            **task.internal_data.pop('extra_data', {})
        )

        yield handler

    @classmethod
    def report_wrong(cls, data):
        return Task(
            url='http://antigate.com/res.php',
            post=[
                ('key', data['key']),
                ('action', 'reportbad'),
                ('id', data['captcha_id'])
            ]
        )
