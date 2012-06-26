# -*- coding: utf-8 -*-

import datetime
from logging import getLogger

from sqlalchemy import create_engine, Column, Integer, String, DateTime, not_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


logger = getLogger('fetcher.proxy_list')


Model = declarative_base()


class Proxy(Model):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True)

    ip = Column(String(24), unique=True)
    used = Column(DateTime)


engine = create_engine('sqlite://')

Model.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class ProxyList(object):
    PROXY_SLEEP_TIME = 60

    @classmethod
    def append_proxies(cls, container):
        if isinstance(container, file):
            container = container.read()

        if isinstance(container, (str, unicode)):
            container = set(container.strip().splitlines())

        if isinstance(container, (set, list, tuple)):
            for line in container:
                line = str(line.strip())

                if line:
                    session.add(
                        Proxy(
                            ip=line
                        )
                    )

            session.commit()

    @classmethod
    def get_proxy(cls):
        ip = ''
        proxy = session.query(Proxy).filter(not_(Proxy.used)).first()
        if not proxy:
            proxy = session.query(Proxy).order_by(Proxy.used.asc()).first()

        if not proxy:
            logger.error(u'Список прокси пуст!')

        else:
            valid = not proxy.used
            if not valid:
                elapsed = datetime.datetime.now() - proxy.used
                print elapsed
                valid = elapsed >= datetime.timedelta(seconds=ProxyList.PROXY_SLEEP_TIME)

            if not valid:
                logger.error('Закончились прокси! Увеличьте таймаут или добавьте еще')

            else:
                ip = proxy.ip
                proxy.used = datetime.datetime.now()
                session.commit()

        return dict(
            proxy=ip,
            proxy_type='HTTP',
            proxy_auth=None
        )
