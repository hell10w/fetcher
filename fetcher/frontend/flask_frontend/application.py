# -*- coding: utf-8 -*-

from os import urandom

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.login import LoginManager


app = Flask(__name__)
app.secret_key = urandom(24)

app.config.setdefault('REDIRECT_AFTER_LOGIN', 'index')
additional_variables = {}

database = SQLAlchemy(app)
model = database.Model

login_manager = LoginManager()
login_manager.setup_app(app)

admin = Admin(app)


@app.context_processor
def _additional_variables():
    return dict(
        (key, value if not callable(value) else value())
        for key, value in additional_variables.iteritems()
    )
