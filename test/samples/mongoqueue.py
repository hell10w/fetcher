from tasks.queues.mongo_queue import MongoQueue

queues = [MongoQueue() for _ in range(10)]

for queue in queues:
    for i in xrange(5000):
        queue.put((10, i))

