# -*- coding: utf-8 -*-

import re

from fetcher.frontend import FlaskFrontend
from fetcher import MultiFetcher, Task, Structure as x


class ProjectsFinder(MultiFetcher):
    def tasks_generator(self):
        #for index in xrange(1, count + 1):
        for index in xrange(1, 2):
            yield Task(
                url='http://www.free-lance.ru/?page=%d' % index,
                handler='page'
            )

    def task_page(self, task, error=None):
        if task.response.code != 200:
            yield task
            return

        task.js.evalScript('function seo_print(text) {document.write(text);}')

        for tag in task.js._findAll('script'):
            if tag.string:
                if tag.string.startswith('seo_print'):
                    print tag.string
                    #print unicode(tag.string)
                    task.js.evalScript(tag.string.encode('ascii', 'backslashreplace'), tag=tag)
            #print tag.string
            #self.evalScript(tag.string, tag=tag)
        print task.js.document


if __name__ == '__main__':
    frontend = FlaskFrontend(ProjectsFinder)
    frontend.run()
