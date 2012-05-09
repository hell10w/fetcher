# -*- coding: utf-8 -*-

from memory_queue import MemoryQueue

try:
    from mongo_queue import MongoQueue
except ImportError:
    MongoQueue = MemoryQueue
