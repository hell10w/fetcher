# -*- coding: utf-8 -*-

from Queue import PriorityQueue
from logging import getLogger
from zlib import compress, decompress
from cPickle import dumps, loads

from base import BaseQueue


logger = getLogger('fetcher.queue.memory')


class Queue(BaseQueue):
    '''Очередь хранящаяся в оперативной памяти'''

    def __init__(self, queue_compress=False, **kwargs):
        self._compress = queue_compress
        self._queue = PriorityQueue()

    def size(self):
        return self._queue.qsize()

    def get(self):
        priority, data = self._queue.get()
        if self._compress:
            data = decompress(data)
        return priority, loads(data)

    def put(self, item):
        priority, data = item[:2]
        data = dumps(data)
        if self._compress:
            data = compress(data)
        self._queue.put((priority, data))
