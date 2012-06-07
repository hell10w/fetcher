# -*- coding: utf-8 -*-

from logging import Handler, getLogger, DEBUG
from threading import Thread
from time import time
from collections import OrderedDict

from flask import Flask, redirect, url_for, render_template, jsonify, request
from flask.ext.login import login_required

from fetcher.tasks import MemoryQueue, MongoQueue

from application import app, database, model, additional_variables
import admin
import login
from models import User
from forms import OptionsForm, CancelForm


fetcher_logger = getLogger('fetcher')
fetcher_logger.setLevel(DEBUG)


class CacheHandler(Handler):
    STORE_SIZE = 10
    items = OrderedDict()

    def emit(self, record):
        now = time()
        CacheHandler.items[now] = (
            now - Frontend.current._start_time,
            record.msg
        )
        if len(CacheHandler.items) > CacheHandler.STORE_SIZE:
            CacheHandler.items.popitem(last=False)


fetcher_logger.addHandler(CacheHandler())


class Frontend(object):
    current = None

    def __init__(self, spider_class, port=None, only_local=False, connection_string=None, *args, **kwargs):
        if Frontend.current:
            Exception('Only single Frontend may exists!')
        Frontend.current = self

        self._spider_class = spider_class
        self._spider = None
        self._thread = None

        parser_name = getattr(self._spider_class, 'name', None)
        if not parser_name:
            parser_name = self._spider_class.__name__
        additional_variables['parser_name'] = parser_name
        additional_variables['spider_working'] = lambda: self.is_spider_working

        self.run_kwargs = {}
        if port:
            self.run_kwargs.setdefault('port', port)
        if not only_local:
            self.run_kwargs.setdefault('host', '0.0.0.0')
        self.run_kwargs.setdefault('debug', True)

        if connection_string:
            app.config['SQLALCHEMY_DATABASE_URI'] = connection_string

    def run(self):
        database.create_all()
        if not User.query.count():
            database.session.add(User('admin', 'admin', True))
            database.session.commit()
        app.run(**self.run_kwargs)

    @property
    def is_spider_working(self):
        if self._spider:
            if self._thread:
                if self._thread.isAlive():
                    return True
            self._spider = None
            self._thread = None
        return False

    @property
    def work_time(self):
        return time() - self._start_time

    def get_statistics(self):
        return [
            'Work time: %.2f seconds' % self.work_time,
            'Queue size: %d' % self._spider.tasks.size()
        ]

    def _start(self, **kwargs):
        try:
            self._start_time = time()
            self._spider = self._spider_class(**kwargs)
            self._thread = Thread(target=self._spider.start)
            self._thread.start()
        except:
            self._spider = None
            self._thread = None
            return False
        else:
            return True

    def _stop(self):
        if self.is_spider_working:
            self._spider.stop()
        return True


@app.route('/start', endpoint='start', methods=['post'])
@login_required
def start():
    form = OptionsForm()
    if form.validate_on_submit():
        options = {}
        if form.queue.data == '0':
            options.setdefault('queue', MemoryQueue)
        elif form.queue.data == '1':
            options.setdefault('queue', MongoQueue)
        options.setdefault('threads_count', int(form.threads_count.data))
        additional_variables['show_log'] = form.debug.data
        Frontend.current._start(**options)
    return redirect(url_for('index'))


@app.route('/stop', endpoint='stop', methods=['post'])
@login_required
def stop():
    form = CancelForm()
    if form.validate_on_submit():
        Frontend.current._stop()
    return redirect(url_for('index'))


@app.route('/', endpoint='index')
@login_required
def index():
    if not Frontend.current.is_spider_working:
        form = OptionsForm()
    else:
        form = CancelForm()
    return render_template('index.html', form=form)


@app.route('/is_working', endpoint='is_working')
@login_required
def is_working():
    return jsonify(result=Frontend.current.is_spider_working)


@app.route('/statistics', endpoint='statistics')
@login_required
def statistics():
    return jsonify(result=Frontend.current.get_statistics())


@app.route('/logs', endpoint='logs')
@login_required
def logs():
    last_time = request.args.get('last_time', 0, type=int)
    result = [
        dict(zip(['offset', 'msg'], value))
        for key, value in CacheHandler.items.iteritems()
        if key > last_time
    ]
    return jsonify(
        result=dict(
            time=time(),
            log=result
        )
    )
