# -*- coding: utf-8 -*-

import logging

from fetcher import MultiFetcher, TasksGroup, Task


class QipRu(MultiFetcher):
    '''def tasks_generator(self):
        for _ in range(10):
            yield Task(
                handler='foo',
                url='http://localhost',
                index=_
            )'''

    def task_foo(self, task, error=None):
        print task.index

    def on_start(self):
        #for task in self.process_tasks_generator():
        #    print task,

        self.tasks.add_task(
            url='http://qip.ru/reg/register',
            handler='main',
            temp_file_options=dict(
                delete_on_finish=False
            )
        )

    def task_main(self, task, error=None):
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
            print '  ', task_result.task.response.body.name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    qip_ru = QipRu()
    qip_ru.start()
