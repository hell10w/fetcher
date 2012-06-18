# -*- coding: utf-8 -*-

from sys import maxint
from Queue import Queue
from cPickle import dumps, loads

from pymongo import Connection, ASCENDING
from pymongo.binary import Binary
from pymongo.errors import CollectionInvalid

from fetcher.errors import FetcherException


class MongoQueue(Queue):
    def __init__(self, queue_database='FetcherQueues', queue_name=None, **kwargs):
        self._database_name = queue_database
        self._collection_name = queue_name
        Queue.__init__(self)

    def __del__(self):
        if not self._collection_name:
            self.clear()

    def _init(self, maxsize):
        connection = Connection()
        database = connection[self._database_name]

        if self._collection_name:
            self.collection = database[self._collection_name]
        else:
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
        item = self.collection.find_and_modify(
            sort={'priority': ASCENDING},
            remove=True
        )
        if not item:
            raise IndexError()
        priority = item.get('priority', 0)
        value = item.get('value', None)
        if value:
            value = loads(value)
        return (priority, value)
