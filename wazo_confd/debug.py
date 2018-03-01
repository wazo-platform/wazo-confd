# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

# https://github.com/mitsuhiko/flask-sqlalchemy
# Copyright 2014-2017 by Armin Ronacher
# SPDX-License-Identifier: BSD-3-Clause

import time

from flask import _app_ctx_stack, current_app
from operator import itemgetter
from sqlalchemy import event


class _DebugQueryTuple(tuple):
    statement = property(itemgetter(0))
    parameters = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))

    @property
    def duration(self):
        return self.end_time - self.start_time


class EngineDebuggingSignalEvents(object):
    """Sets up handlers for two events that let us track the execution time of
    queries."""

    def __init__(self, engine, import_name):
        self.engine = engine
        self.app_package = import_name

    def register(self):
        event.listen(
            self.engine, 'before_cursor_execute', self.before_cursor_execute
        )
        event.listen(
            self.engine, 'after_cursor_execute', self.after_cursor_execute
        )

    def before_cursor_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        if current_app:
            context._query_start_time = time.time()

    def after_cursor_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        if current_app:
            try:
                queries = _app_ctx_stack.top.sqlalchemy_queries
            except AttributeError:
                queries = _app_ctx_stack.top.sqlalchemy_queries = []

            queries.append(_DebugQueryTuple((
                statement, parameters, context._query_start_time, time.time()
            )))


def get_debug_queries():
    return getattr(_app_ctx_stack.top, 'sqlalchemy_queries', [])
