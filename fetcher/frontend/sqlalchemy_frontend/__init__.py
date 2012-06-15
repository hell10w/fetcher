# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Model = declarative_base()


def create_session(connection_string):
    engine = create_engine(connection_string)

    Model.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return engine, session
