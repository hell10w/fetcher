# -*- coding: utf-8 -*-

import logging

from fetcher import MultiFetcher, TasksGroup


class QipRu(MultiFetcher):
    def on_start(self):
        self.tasks.add_task(
            url='http://qip.ru/reg/register',
            handler='main'
        )

    def task_main(self, task, error=None):
        print '!!!!!!!!!!!!!!!!!!!!!'
        task.make_links_absolute()
        scripts = task.xpath_list('//script[@src]/@src')

        '''yield TasksGroup(
            task=task,
            urls=scripts,
            handler='main'
        )'''

        self.tasks.add_group(
            task=task,
            urls=scripts,
            handler='main'
        )

        print scripts
        #print task.js
        #task.js.fireOnloadEvents()
        #print dir(task.js.document)

    def group_main(self, group):
        print group
        print group.finished_tasks
        for url, task_result in group.finished_tasks.iteritems():
            print url, task_result.task, task_result.error


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    qip_ru = QipRu()
    qip_ru.start()
