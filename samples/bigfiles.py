from fetcher.multifetch import MultiFetcher


class Worker(MultiFetcher):
    def __init__(self, **kwargs):
        super(Worker, self).__init__(**kwargs)

        for _ in xrange(30):
            self.tasks.add_task(
                url='http://localhost/12345678',
                handler='loaded'
            )

    def task_loaded(self, task):
        print task.response.url
        print '  ', task.response.body.name


worker = Worker()
worker.start()
