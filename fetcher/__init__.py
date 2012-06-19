# -*- coding: utf-8 -*-

from cache import FileCacheBackend, MongoCacheBackend, MySQLCacheBackend, CACHE_NONE, CACHE_RESPONSE, CACHE_TRUE
from errors import FetcherException
from fetch import Structure, Chunk, Request, Response, AUTO_RESPONSE_BODY, MEMORY_RESPONSE_BODY, FILE_RESPONSE_BODY
from tasks import Task, TaskResult, TasksGroup, Tasks, MemoryQueue, MongoQueue
from multifetch import MultiFetcher


VERSION = (0, 0, 5)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
