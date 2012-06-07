# -*- coding: utf-8 -*-

from fetcher import MultiFetcher, Task, Structure as x


class LogsScanner(MultiFetcher):
    #START_URL = 'http://0xd34df00d.me/logs/chat/'
    START_URL = 'http://0xd34df00d.me/logs/chat/javascript%40conference.jabber.ru/2009/12/18.html'

    def on_start(self):
        yield Task(
            url=LogsScanner.START_URL,
            handler='lookup'
        )

    def task_lookup(self, task, error=None):
        if task.response.status_code != 200:
            yield task
            return

        task.make_links_absolute()

        if task.xpath_exists('//div[@class="roomtitle"]'):
            name = task.xpath('//div[@class="roomtitle"]/text()')
            date = task.xpath('//div[@class="logdate"]/text()')
            jid = task.xpath('//a[@class="roomjid"]/text()')
            print '%s (%s), %s' % (name, jid, date)

            items = task.structured_xpath(
                '//a[@class="ts"]',
                x(
                    './following-sibling::font',
                    class_='./@class',
                    message='./text()',
                    text='./following-sibling::text()'
                ),
                time='./@name'
            )

            for item in items:
                print '%s %3s | %s%s' % (
                    item.time, item.class_,
                    item.message,
                    '' if item.class_ != 'mn' else ': ' + item.text
                )
        else:
            for link in task.xpath_list('//a/@href'):
                link = str(link)
                if link.startswith(LogsScanner.START_URL):
                    yield Task(
                        url=link,
                        handler='lookup'
                    )


if __name__ == '__main__':
    l = LogsScanner()
    l.start()
