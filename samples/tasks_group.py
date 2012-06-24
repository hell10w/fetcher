# -*- coding: utf-8 -*-

import logging

from fetcher import MultiFetcher, TasksGroup, Task


class QipRu(MultiFetcher):
    def tasks_generator(self):
        yield Task(
            url='http://qip.ru/reg/register',
            handler='main'
        )

    def task_main(self, task, error=None):
        task.html.make_links_absolute()
        scripts = task.html.xpath('//script[@src]/@src', all=True)

        print scripts

        yield TasksGroup(
            task=task,
            urls=scripts,
            handler='main'
        )

    def group_main(self, group):
        loaded_scripts = group.finished_tasks

        scripts = group.task.html.xpath('//script[@src]', all=True)

        for script in scripts:
            remote_script_task = loaded_scripts[script.attrib['src']].task
            remote_script = remote_script_task.response.content
            script.text = remote_script
            del script.attrib['src']


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    qip_ru = QipRu()
    qip_ru.start()
    qip_ru.render_stat()
