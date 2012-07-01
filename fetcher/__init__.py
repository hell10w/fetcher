# -*- coding: utf-8 -*-

from cache import CACHE_NONE, CACHE_RESPONSE, CACHE_TRUE
from fetch import Structure, Chunk, Request, Response, \
                  AUTO_RESPONSE_BODY, MEMORY_RESPONSE_BODY, FILE_RESPONSE_BODY, \
                  PostFile
from tasks import Task, TasksGroup, Tasks, DataItem
from multifetch import MultiFetcher, TimeoutError, ConnectionError, AuthError, NetworkError


VERSION = (0, 0, 8)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
