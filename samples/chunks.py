# -*- coding: utf-8 -*-

import re
import datetime
from logging import getLogger

from fetcher import MultiFetcher, Task, Structure as x


logger = getLogger('weblancer_net')


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

        task.html.make_links_absolute()

        if self.LOOKUP_ALL_PAGES:
            pages = task.html.xpath('//div[contains(@class, "pages_list")]/a/@href', all=True)
            for url in pages:
                if url not in self.looked_pages:
                    yield Task(
                        task=task,
                        handler='page',
                        url=url
                    )
                    self.looked_pages.append(url)

        projects = task.html.structured_xpath(
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

        for p in projects:
            for key, value in p.iteritems():
                print '%-11s: %s' % (key, value)
            print '*' * 20

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
    worker = WebLancerNet()
    worker.start()
    worker.render_stat()
