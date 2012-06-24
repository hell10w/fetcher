# -*- coding: utf-8 -*-

from logging import getLogger, DEBUG, basicConfig

from fetcher import MultiFetcher, Request, Task


logger = getLogger('torchecker')


Request.proxy = 'localhost:9050'
Request.proxy_type = 'SOCKS5'
Request.connection_timeout = 3
Request.overall_timeout = 5


class TorWorker(MultiFetcher):
    def on_start(self):
        self.count = 0
        self.ip = set()
        for _ in range(100):
            yield Task(
                url='http://www.whatsmyip.us/',
                handler='whatsmyip'
            )

    def task_whatsmyip(self, task, error=None):
        if error or task.response.status_code != 200:
            logger.error(
                u'Подключение не удалось с кодом %s или ошибкой %s' % (
                    task.response.status_code,
                    error
                )
            )
            yield task
            return

        try:
            ip = task.xpath('id("do")/text()').strip()
            self.count += 1
            if ip not in self.ip:
                print 'IP: %s, выполненных задач: %d' % (ip, self.count)
                self.count = 0
            self.ip.add(ip)
        except:
            pass


if __name__ == '__main__':
    basicConfig(level=DEBUG)

    worker = TorWorker(
        threads_count=50
    )
    worker.start()
