# -*- coding: utf-8 -*-

import flaskext.wtf as wtf


class LoginForm(wtf.Form):
    login = wtf.TextField(u'Login', [wtf.Required()])
    password = wtf.PasswordField(u'Password', [wtf.Required()])
    submit = wtf.SubmitField(u'Login')


class CancelForm(wtf.Form):
    pass


class OptionsForm(wtf.Form):
    queue = wtf.SelectField(
        u'Tasks queue type',
        choices=[('0', 'Memory'), ('1', 'Mongo')]
    )
    threads_count = wtf.SelectField(
        u'Threads count',
        choices=[(str(_), str(_)) for _ in range(1, 101)]
    )
    debug = wtf.BooleanField(u'Debug')
