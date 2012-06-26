# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from fetcher.utils import url_fix


Model = declarative_base()


class Url(Model):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    url = Column(Text) # протокол не лимитирует длину URL


engine = create_engine('sqlite://')

Model.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class LookedUrls(object):
    @classmethod
    def is_exists(cls, url):
        url = url_fix(url)
        if not session.query(Url).filter_by(url=url).first():
            session.add(Url(url=url))
            session.commit()
            return False
        return True

    @classmethod
    def clear_all(cls):
        session.query(Url).delete()
        session.commit()
