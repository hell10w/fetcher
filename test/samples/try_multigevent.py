import time
import multiprocessing
import gevent
import gevent.pool
import requests
from tasks.queues.mongo_queue import MongoQueue


queue = MongoQueue()
# multiprocessing.Queue()
for _ in xrange(1500):
    queue.put((0, 'http://localhost'))


class WorkProcess(multiprocessing.Process):
    def __init__(self):
        super(WorkProcess, self).__init__()
        self.daemon = True
        self.count = 0
        self.start()

    def run(self):
        gevent.reinit()
        pool = gevent.pool.Pool(size=30)
        while not queue.empty():
            def callback(resp):
                self.count += 1
            _, url = queue.get()
            pool.apply_async(requests.get, args=(url,), callback=callback)
            pool.wait_available()
        pool.join()


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    start = time.time()
    processes = [WorkProcess() for _ in range(4)]
    for process in processes:
        process.join()
        print process.count,
    print
    print time.time() - start

