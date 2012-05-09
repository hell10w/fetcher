# -*- coding: utf-8 -*-

from sys import maxint
from Queue import Queue
from cPickle import dumps, loads

from pymongo import Connection, ASCENDING
from pymongo.binary import Binary
from pymongo.errors import CollectionInvalid

from errors import FetcherException


class MongoQueue(Queue):
    def __init__(self, **kwargs):
        self.database_name = kwargs.pop('database', 'MongoQueue')
        self.collection_name = kwargs.pop('name', None)
        self.clear_on_init = kwargs.pop('clear_on_init', False)
        self.clear_on_del = kwargs.pop('clear_on_del', False)

        Queue.__init__(self, maxsize=kwargs.pop('maxsize', 0))

    def __del__(self):
        if self.clear_on_del:
            self.clear()

    def _init(self, maxsize):
        connection = Connection()
        database = connection[self.database_name]

        if self.collection_name:
            self.collection = database[self.collection_name]
            if self.clear_on_init:
                self.clear()
        else:
            self.clear_on_init = False
            self.clear_on_del = True

            def create_collection():
                for index in xrange(maxint):
                    name = 'queue_%d' % index
                    try:
                        collection = database.create_collection(name)
                    except CollectionInvalid:
                        pass
                    else:
                        return collection
                raise FetcherException()

            self.collection = create_collection()

    def clear(self):
        self.collection.drop()

    def _qsize(self, len=len):
        return self.collection.count()

    def _put(self, item):
        priority, value = item[:2]
        item = {
            'value': Binary(dumps(value)),
            'priority': priority
        }
        self.collection.save(item)

    def _get(self):
        priority, value = 0, None
        try:
            item = self.collection.find_and_modify(
                sort={'priority': ASCENDING},
                remove=True
            )
            priority = item.get('priority', 0)
            value = item.get('value', None)
            if value:
                value = loads(value)
        finally:
            return (priority, value)
