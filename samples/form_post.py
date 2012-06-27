# -*- coding: utf-8 -*-

from logging import getLogger, basicConfig, DEBUG

from fetcher import MultiFetcher, Task, PostFile


logger = getLogger('filepost')


class FilePoster(MultiFetcher):
    def on_start(self):
        logger.debug(u'Добавление инициирующей задачи')
        yield Antigate.send(
            handler='result',
            key='???????????????',
            filename='/tmp/0.jpg',
            phrase=True
        )

    def task_result(self, task, error=None):
        state_task = Antigate.send_handler(task, error, handler='answer')
        if not state_task:
            # капча отправлена с ошибкой - нужно повторить
            yield task
        else:
            # капча успешно отправлена - можно запрашивать её статус
            yield state_task

    def task_answer(self, task, error=None):
        result, error_message = Antigate.state_handler(task, error)

        if result or error_message:
            # если установно значение в result или error_message - то либо капча разгадана, либо произошла ошибка
            print result, error_message
            return

        # капча еще не разгадана - повтор запроса статуса
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
