# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for
from flask.ext.login import current_user, login_required, login_user, logout_user

from application import app, login_manager, additional_variables
from models import User
from forms import LoginForm


login_manager.login_view = 'login'
additional_variables['user'] = lambda: current_user


@login_manager.user_loader
def user_by_id(id):
    user = User.query.filter_by(id=id).first()
    return user


def validate_user(login, password):
    user = User.query.filter_by(login=login, password=password).first()
    return user


@app.route('/login', endpoint='login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))

    bad_login = False
    unknown_error = False

    form = LoginForm()
    if form.validate_on_submit():
        user = validate_user(form.login.data, form.password.data)
        if user:
            if login_user(user, force=True):
                return redirect(url_for(app.config['REDIRECT_AFTER_LOGIN']))
            else:
                unknown_error = True
        else:
            bad_login = True

    return render_template(
        'login.html',
        form=form,
        bad_login=bad_login,
        unknown_error=unknown_error
    )


@app.route('/logout', endpoint='logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
