# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from flask import Flask, g, request
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from xivo import http_helpers

from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.infos import dao as info_dao

from xivo_confd import plugin_manager
from xivo_confd.authentication.confd_auth import auth
from xivo_confd.core_rest_api import CoreRestApi
from xivo_confd.helpers.common import handle_error
from xivo_confd.helpers.restful import ConfdApi
from xivo_confd.helpers.bus_publisher import BusPublisher
from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher

logger = logging.getLogger(__name__)

app = Flask('xivo_confd')

api = ConfdApi(app, prefix="/1.1")


def get_bus_publisher():
    publisher = g.get('bus_publisher')
    if not publisher:
        publisher = g.bus_publisher = BusPublisher.from_config(app.config)
    return publisher


def get_sysconfd_publisher():
    publisher = g.get('sysconfd_publisher')
    if not publisher:
        publisher = g.sysconfd_publisher = SysconfdPublisher.from_config(app.config)
    return publisher


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
    flush_sysconfd()
    flush_bus()
    return http_helpers.log_request(response)


@app.before_first_request
def load_uuid():
    with session_scope():
        app.config['uuid'] = info_dao.get().uuid


def commit_database():
    try:
        Session.commit()
    except SQLAlchemyError:
        Session.rollback()
        raise
    finally:
        Session.remove()


def flush_sysconfd():
    publisher = g.get('sysconfd_publisher')
    if publisher:
        publisher.flush()


def flush_bus():
    publisher = g.get('bus_publisher')
    if publisher:
        publisher.flush()


@app.errorhandler(Exception)
def error_handler(error):
    return handle_error(error)


def setup_app(config):
    app.secret_key = os.urandom(24)
    app.config.update(config)

    http_helpers.add_logger(app, logger)

    app.debug = config.get('debug', False)

    auth.set_config(config)
    core = CoreRestApi(app, api, auth)
    plugin_manager.load_plugins(core)

    load_cors(app)

    return app


def load_cors(app):
    cors_config = dict(app.config['rest_api'].get('cors', {}))
    enabled = cors_config.pop('enabled', False)
    if enabled:
        CORS(app, **cors_config)
