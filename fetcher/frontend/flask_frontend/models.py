# -*- coding: utf-8 -*-

from flask.ext.login import UserMixin

from application import app, database, model


app.config['SQLALCHEMY_BINDS'] = {'spider_users': 'sqlite:///spider_users.db'}


class User(model, UserMixin):
    __bind_key__ = 'spider_users'

    id = database.Column(database.Integer, primary_key=True)

    login = database.Column(database.String(12), unique=True)
    password = database.Column(database.String(24))

    admin = database.Column(database.Boolean())

    def __init__(self, login=None, password=None, admin=False):
        self.login = login
        self.password = password
        self.admin = admin
