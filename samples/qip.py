# -*- coding: utf-8 -*-

import logging

from fetcher import MultiFetcher, TasksGroup, Task


class QipRu(MultiFetcher):
    def tasks_generator(self):
        self.tasks.add_task(
            url='http://qip.ru/reg/register',
            handler='main',
            temp_file_options=dict(delete_on_finish=False)
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
        loaded_scripts = group.finished_tasks
        print loaded_scripts
        scripts = group.task.xpath_list('//script[@src]')
        for script in scripts:
            code = loaded_scripts[script.attrib['src']].task.response.get_unicode_body()
            script.text = code
            del script.attrib['src']
            #print dir(script)
            #
            #group.task.html_replace(script, '<script type="text/javascript">' + .decode('utf-8') + '</script>')
        #print group.task.html_content()
        print group.task.html_tree.text
        print group.task.save_html_content().name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    qip_ru = QipRu()
    qip_ru.start()
