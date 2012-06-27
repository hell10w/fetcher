# -*- coding: utf-8 -*-

from logging import getLogger, basicConfig, DEBUG

from fetcher import MultiFetcher, Task, PostFile


logger = getLogger('filepost')


class AntigateTask(object):
    def __init__(self, key=None, filename=None,
                       phrase=False, regsense=False, numeric=False,
                       min_len=0, max_len=30):

        if not key:
            raise Exception(u'Ключ для Antigate должен быть указан!')

        if not filename:
            raise Exception(u'Не указан файл капчи!!')

        self.captcha_id = None

        self.key = key
        self.filename = filename
        self.phrase = '1' if phrase else '0'
        self.regsense = '1' if regsense else '0'
        self.numeric = '1' if numeric else '0'
        self.min_len = str(min_len)
        self.max_len = str(max_len)

    def send(self, **kwargs):
        post = [
            ('method', 'post'),
            ('phrase', self.phrase),
            ('regsense', self.regsense),
            ('numeric', self.numeric),
            ('min_len', self.min_len),
            ('max_len', self.max_len),
            ('key', self.key),
            ('file', PostFile(filename=self.filename))
        ]

        return Task(
            url='http://antigate.com/in.php',
            method='POST',
            is_multipart_post=True,
            post=post,
            **kwargs
        )

    def send_handler(self, task, error=None):
        if error or task.response.status_code != 200:
            return False
        try:
            self.captcha_id = int(task.response.content.split('|')[1])
            return True
        except:
            return False

    def state(self, **kwargs):
        if not self.captcha_id:
            raise Exception(u'Нет id капчи - обработчик задачи отправки не вызывался или отработал с ошибкой!')
        return Task(
            url='http://antigate.com/res.php',
            post=[
                ('key', self.key),
                ('action', 'get'),
                ('id', self.captcha_id)
            ],
            **kwargs
        )

    def state_handler(self, task, error=None):
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


class FilePoster(MultiFetcher):
    def on_start(self):
        logger.debug(u'Добавление инициирующей задачи')
        self.a = AntigateTask(
            key='***********************',
            filename='/tmp/0.jpg',
            phrase=True,
        )
        yield self.a.send(handler='result')

    def task_result(self, task, error=None):
        if not self.a.send_handler(task, error):
            yield task

        yield self.a.state(handler='answer')

    def task_answer(self, task, error=None):
        result, error_message = self.a.state_handler(task, error)

        if result or error_message:
            print result, error_message
            return

        yield task

    def task_main(self, task, error=None):
        if task.response.status_code != 200 or error:
            logger.debug(u'Ошибка при выполнении инициирующей задачи!')
            yield task
            return

        task.get_control('submitter').value = 'developer'
        task.submit(
            files=[('pics', PostFile(filename='form_post.py'))]
        )
        yield task.setup(
            handler='posted'
        )

    def task_posted(self, task, error=None):
        if task.response.status_code != 200 or error:
            logger.debug(u'Ошибка при выполнении POST-запроса!')
            yield task
            return

        logger.info(u'POST-запрос выполнен')
        return


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    worker = FilePoster(threads_count=3)
    worker.start()
    worker.render_stat()
