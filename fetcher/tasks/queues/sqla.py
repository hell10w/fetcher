# -*- coding: utf-8 -*-

from time import time, sleep
from logging import getLogger
from zlib import compress, decompress
from cPickle import dumps, loads

from sqlalchemy import create_engine, Column, Integer, BLOB, not_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from base import BaseQueue


logger = getLogger('fetcher.queue.sqla')


Session = sessionmaker()
Base = declarative_base()


class QueueItem(Base):
    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True)

    timeon = Column(Integer)
    priority = Column(Integer)
    data = Column(BLOB)


class Queue(BaseQueue):
    '''Очередь хранящаяся в БД через SQLAlchemy'''

    def __init__(self, queue_uri=None, **kwargs):
        if not queue_uri:
            queue_uri = 'sqlite://'
            logger.warning(u'Не указан URI для подключения к БД!\nБудет использоваться SQLite с таблицей в оперативной памяти!')

        engine = create_engine(queue_uri)
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)

        self.session = Session()

    def size(self):
        return self.session.query(QueueItem).count()

    def get(self):
        while self.size():
            item = self.session.query(QueueItem).\
                                filter(QueueItem.timeon <= time()).\
                                order_by(QueueItem.priority).\
                                first()

            if not item:
                item = self.session.query(QueueItem).\
                                    filter_by(timeon=None).\
                                    order_by(QueueItem.priority).\
                                    first()
            if item:
                self.session.delete(item)
                return item.priority, loads(decompress(item.data))

            sleep(0.1)

    def put(self, item):
        priority, value = item[:2]

        timeon = getattr(value, 'timeon', None)
        if timeon:
            timeon += time()

        self.session.add(
            QueueItem(
                priority=priority,
                data=compress(dumps(value)),
                timeon=timeon
            )
        )
        self.session.commit()
