# -*- coding: utf-8 -*-

import sqlalchemy as database
from sqlalchemy.ext.declarative import declarative_base


engine = None
model = declarative_base()


def create_connection(connection_string):
    engine = database.create_engine(connection_string, echo=False)
