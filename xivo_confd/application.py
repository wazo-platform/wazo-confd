# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import logging
import urllib

from flask import Flask, request
from flask_cors import CORS

from sqlalchemy.exc import SQLAlchemyError

from xivo import http_helpers

from xivo_dao.helpers.db_manager import Session

from xivo_confd import plugin_manager
from xivo_confd.core_rest_api import CoreRestApi
from xivo_confd.authentication.confd_auth import ConfdAuth
from xivo_confd.helpers.common import handle_error
from xivo_confd.helpers.restful import ConfdApi

logger = logging.getLogger(__name__)

app = Flask('xivo_confd')

api = ConfdApi(app, prefix="/1.1")

auth = ConfdAuth()


@app.before_request
def log_requests():
    url = request.url.encode('utf8')
    url = urllib.unquote(url)
    params = {
        'method': request.method,
        'url': url,
    }
    if request.data:
        params.update({'data': request.data})
        logger.info("%(method)s %(url)s with data %(data)s ", params)
    else:
        logger.info("%(method)s %(url)s", params)


@app.after_request
def after_request(response):
    commit_database()
    return http_helpers.log_request(response)


def commit_database():
    try:
        Session.commit()
    except SQLAlchemyError:
        Session.rollback()
        raise
    finally:
        Session.remove()


@app.errorhandler(Exception)
def error_handler(error):
    Session.rollback()
    return handle_error(error)


def create_app(config):
    app.secret_key = os.urandom(24)
    app.config.update(config)

    http_helpers.add_logger(app, logger)

    app.debug = config.get('debug', False)

    core = CoreRestApi(app, api, auth)
    plugin_manager.load_plugins(core)

    load_cors(app)

    return app


def load_cors(app):
    cors_config = dict(app.config['rest_api'].get('cors', {}))
    enabled = cors_config.pop('enabled', False)
    if enabled:
        CORS(app, **cors_config)
