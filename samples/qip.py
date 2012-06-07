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
        task.make_links_absolute()
        scripts = task.xpath_list('//script[@src]/@src')

        print scripts

        yield TasksGroup(
            task=task,
            urls=scripts,
            handler='main'
        )

    def group_main(self, group):
        task = group.task
        loaded_scripts = group.finished_tasks

        scripts = group.task.xpath_list('//script[@src]')

        for script in scripts:
            remote_script_task = loaded_scripts[script.attrib['src']].task
            remote_script = remote_script_task.response.get_unicode_body()
            script.text = remote_script
            del script.attrib['src']

        group.task.response.body = group.task.save_html_content()
        del group.task.response.__dict__['_body']

        task.choose_form(1)
        print task.form_fields()


        task.js.fireOnloadEvents()

        #for form in task.forms:
        #    print dict(form.fields)

        #print group.task.save_html_content().name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    qip_ru = QipRu()
    qip_ru.start()
