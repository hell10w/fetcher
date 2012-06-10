# -*- coding: utf-8 -*-

import re
import datetime
from logging import getLogger

from fetcher import MultiFetcher, Task, Structure as x, Chunk as c
from fetcher.frontend.flask_frontend import Frontend, app, database, model


WORKER_IN_FRONTEND = True
CONNECTION_STRING = 'sqlite:///projects.db'

logger = getLogger('fetcher.weblancer_net')


category_project = database.Table('projects',
    database.Column('category_id', database.Integer, database.ForeignKey('category.id')),
    database.Column('project_id', database.Integer, database.ForeignKey('project.id'))
)

class Category(model):
    id = database.Column(database.Integer, primary_key=True)

    url = database.Column(database.String(255), unique=True)
    name = database.Column(database.String(255))

    projects = database.relationship('Project', backref=database.backref('categories'))

    #subcategories = database.relationship('Category', backref='person', lazy='dynamic')

    def __repr__(self):
        return '<Категория %s>' % self.name


class Project(model):
    id = database.Column(database.Integer, primary_key=True)

    url = database.Column(database.String(80), unique=True)
    name = database.Column(database.Text)

    cost = database.Column(database.String(25))
    answers = database.Column(database.Integer)
    time = database.Column(database.DateTime)

    def __repr__(self):
        return '<Project %s>' % self.url


class WebLancerNet(MultiFetcher):
    LOOKUP_ALL_PAGES = False
    TIME_FORMAT = re.compile(u' \| (\S+) в (\d+):(\d+)', re.U)

    def on_start(self):
        self.looked_pages = []
        yield Task(
            url='http://www.weblancer.net/projects/',
            handler='page'
        )

    def task_page(self, task, error=None):
        if task.response.status_code != 200:
            yield task
            return

        task.make_links_absolute()

        if self.LOOKUP_ALL_PAGES:
            pages = task.xpath_list('//div[contains(@class, "pages_list")]/a/@href')
            for url in pages:
                if url not in self.looked_pages:
                    yield Task(
                        task=task,
                        handler='page',
                        url=url
                    )
                    self.looked_pages.append(url)

        projects = task.structured_xpath(
            '//table[@class="items_list"]/tbody/tr[not(position()=1)]',
            x(
                './td[1]',
                x(
                    './a[1]',
                    name='./text()',
                    url='./@href'
                ),
                time=(
                    './div[1]/noindex[last()]/following-sibling::text()',
                    self.weblancer_time
                )
            ),
            cost='./td[2]/*[1]/text()',
            answers=('./td[3]/text()', int)
        )

        for project in projects:
            if not Project.query.filter_by(url=project.url).count():
                items = [(key, value) for key, value in project.iteritems() if key != 'categories']
                items = dict(items)
                items['categories'] = [
                    Category(**dict(category.iteritems()))
                    for category in project.categories
                ]
                database.session.add(Project(**items))
            database.session.commit()

        '''print len(projects)
        for p in projects:
            print '-' * 20
            for key, value in p.iteritems():
                print '%-11s: %s' % (key, value)'''

    def weblancer_time(self, value):
        try:
            date, hour, minute = re.search(self.TIME_FORMAT, unicode(value)).groups()
            if date == u'сегодня':
                date = datetime.datetime.today()
            elif date == u'вчера':
                date = datetime.datetime.today() - datetime.timedelta(1)
            else:
                date = datetime.datetime.strptime(date, '%d.%m.%Y')
            return date.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        except:
            pass


if __name__ == '__main__':
    frontend = Frontend(
        WebLancerNet,
        connection_string=CONNECTION_STRING
    )
    frontend.add_view(Category)
    frontend.add_view(Project)

    if not WORKER_IN_FRONTEND:
        database.create_all()
        worker = WebLancerNet()
        worker.start()
    else:
        frontend.run()
