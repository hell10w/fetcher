# -*- coding: utf-8 -*-

from fetcher.tasks.queues.memory_queue import MemoryQueue

try:
    from fetcher.tasks.queues.mongo_queue import MongoQueue
except ImportError:
    MongoQueue = MemoryQueue
