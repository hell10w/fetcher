# -*- coding: utf-8 -*-

from fetcher import MultiFetcher, Request


Request.proxy = 'localhost:9050'
Request.proxy_type = 'SOCKS5'


class TorWorker(MultiFetcher):
    def on_start(self):
        self.count = 0
        self.ip = set()
        for _ in range(100):
            self.tasks.add_task(
                url='http://www.whatsmyip.us/',
                handler='whatsmyip'
            )

    def task_whatsmyip(self, task):
        try:
            ip = task.xpath('id("do")/text()').strip()
            self.count += 1
            if ip not in self.ip:
                print ip, self.count
                self.count = 0
            self.ip.add(ip)
        except:
            pass
        self.tasks.add_task(task=task)

if __name__ == '__main__':
    worker = TorWorker(
        threads_count=50
    )
    worker.start()
