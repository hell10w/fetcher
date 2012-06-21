from sys import exit
import logging

from lxml.html import tostring, submit_form
from fetcher import MultiFetcher, TasksGroup, Task


class FuckOff(MultiFetcher):
    def tasks_generator(self):
        yield Task(
            url='http://localhost',
            handler='main'
        )

    def task_main(self, task, error=None):
        task.submit()

        print task.request.url
        print task.request.method
        print task.request.post


        yield task.clone(
            handler='result'
        )

        return

        task.make_links_absolute()
        scripts = task.xpath_list('//script[@src]/@src')

        print scripts

        yield TasksGroup(
            task=task,
            urls=scripts,
            handler='main'
        )

    def task_result(self, task, error=None):
        print error, task.response.status_code
        print '>>result>>'
        task.html.open_in_browser()

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
        #del group.task.response.__dict__['_body']

        #task.choose_form(1)
        #print task.form_fields()


        #task.js.fireOnloadEvents()

        #for form in task.forms:
        #    print dict(form.fields)

        #print group.task.save_html_content().name


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    fo = FuckOff()
    fo.start()
