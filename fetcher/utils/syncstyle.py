# -*- coding: utf-8 -*-

from fetcher import MultiFetcher, Task


_spider = None
_spider_options = {}


class _SyncSpider(MultiFetcher):
    def __init__(self, **kwargs):
        self.yield_item = None
        self.result = None
        super(_SyncSpider, self).__init__(**kwargs)

    def on_start(self):
        yield self.yield_item

    def tasks_collector(self, task, error=None):
        self.result = (task, error)

    def groups_collector(self, group):
        self.result = list(group)

    def data_collector(self, **kwargs):
        self.result = kwargs


def set_options(**kwargs):
    global _spider
    global _spider_options
    _spider_options = kwargs
    if _spider:
        _spider = None


def make(item):
    global _spider
    if not _spider:
        _spider = _SyncSpider(**_spider_options)
    _spider.yield_item = item
    _spider.start()
    return _spider.result


if __name__ == '__main__':
    print make(Task(url='http://localhost'))
    # >> (<fetcher.tasks.Task object at 0x9e9124c>, None)
