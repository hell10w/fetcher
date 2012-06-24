# -*- coding: utf-8 -*-

from sys import maxint
from logging import getLogger
from zlib import compress, decompress
from cPickle import dumps, loads

from pymongo import Connection, ASCENDING
from pymongo.binary import Binary
from pymongo.errors import CollectionInvalid

from base import BaseQueue


logger = getLogger('fetcher.queue.mongo')


class Queue(BaseQueue):
    '''Очередь хранящаяся в Mongo'''

    def __init__(self, queue_database='FetcherQueues', queue_name=None, **kwargs):
        self._database_name = queue_database
        self._collection_name = queue_name

        connection = Connection()
        database = connection[self._database_name]

        if self._collection_name:
            self._collection = database[self._collection_name]

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
                raise Exception(u'Нет свободного имени для коллекции в базе данных!\nУстановите параметр queue_name!')

            self._collection = create_collection()

    def __del__(self):
        if not self._collection_name:
            logger.info(u'Удаление очереди из БД.')
            self._collection.drop()
        else:
            logger.info(u'Очередь остается в БД. В очереди %d заданий.' % self.size())

    def size(self):
        return self._collection.count()

    def get(self):
        item = self._collection.find_and_modify(
            sort={'priority': ASCENDING},
            remove=True
        )
        priority = item.get('priority', 0)
        value = item.get('value', None)
        if value:
            value = loads(decompress(value))
        return (priority, value)

    def put(self, item):
        priority, value = item[:2]
        self._collection.save(
            {
                'value': Binary(compress(dumps(value))),
                'priority': priority
            }
        )
