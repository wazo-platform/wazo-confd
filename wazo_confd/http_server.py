# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging

from cheroot import wsgi
from flask import Flask, g
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.contrib.fixers import ProxyFix

from xivo import http_helpers
from xivo.http_helpers import ReverseProxied
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.infos import dao as info_dao

from ._bus import BusPublisher
from ._sysconfd import SysconfdPublisher
from .helpers.converter import FilenameConverter
from .helpers.restful import auth_verifier

logger = logging.getLogger(__name__)
app = Flask('wazo_confd')
api = Api(app, prefix="/1.1")
_do_not_log_data_endpoints = []


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


def log_requests():
    return http_helpers.log_before_request()


def after_request(response):
    commit_database()
    flush_sysconfd()
    flush_bus()
    return http_helpers.log_request(response)


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


def load_uuid():
    with session_scope():
        app.config['uuid'] = info_dao.get().uuid


class HTTPServer:

    def __init__(self, global_config):
        self.config = global_config['rest_api']
        http_helpers.add_logger(app, logger)

        app.before_first_request(load_uuid)
        app.before_request(log_requests)
        app.after_request(after_request)

        app.secret_key = os.urandom(24)
        app.url_map.converters['filename'] = FilenameConverter

        app.config.update(global_config)
        app.config['MAX_CONTENT_LENGTH'] = 40 * 1024 * 1024

        auth_verifier.set_config(global_config['auth'])
        self._load_cors()
        self.server = None

    def _load_cors(self):
        cors_config = dict(self.config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(app, **cors_config)

    def run(self):
        if self.config['profile']:
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir=self.config['profile'])

        wsgi_app = ReverseProxied(ProxyFix(wsgi.WSGIPathInfoDispatcher({'/': app})))

        bind_addr = (self.config['listen'], self.config['port'])
        self.server = wsgi.WSGIServer(bind_addr=bind_addr, wsgi_app=wsgi_app)
        self.server.ssl_adapter = http_helpers.ssl_adapter(
            self.config['certificate'],
            self.config['private_key'],
        )
        logger.debug(
            'WSGIServer starting... uid: %s, listen: %s:%s',
            os.getuid(),
            bind_addr[0],
            bind_addr[1]
        )
        for route in http_helpers.list_routes(app):
            logger.debug(route)

        try:
            self.server.start()
        except KeyboardInterrupt:
            logger.warning('Stopping wazo-confd: KeyboardInterrupt')
            self.server.stop()

    def stop(self):
        if self.server:
            self.server.stop()
