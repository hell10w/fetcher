# -*- coding: utf-8 -*-

from flask.ext.login import current_user
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.admin import AdminIndexView

from application import database, admin
from models import User


class ProtectedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.admin


class ProtectedAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()


admin.index_view = ProtectedAdminView()
admin.add_view(ProtectedView(User, database.session, name=u'Parser users'))
