# -*- coding: utf-8 -*-

from errors import FetcherException
from fetch import Structure, Request
from tasks import Task, TaskResult, TasksGroup, Tasks, MemoryQueue, MongoQueue
from multifetch import MultiFetcher


VERSION = (0, 0, 3)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Alexey Gromov"
