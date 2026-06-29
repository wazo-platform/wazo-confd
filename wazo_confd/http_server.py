# Copyright 2016-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import os
import socket
from typing import TYPE_CHECKING, Union

from flask import Flask, g
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix
from xivo import http_helpers, wsgi
from xivo.http_helpers import ReverseProxied
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.infos import dao as info_dao

from ._bus import BusPublisher
from ._sysconfd import SysconfdPublisher
from .helpers.converter import FilenameConverter

if TYPE_CHECKING:
    from cheroot.ssl import Adapter

BindAddr = Union[tuple[str, int], str, bytes]

logger = logging.getLogger(__name__)
app = Flask('wazo_confd')
api = Api(app, prefix="/1.1")
_do_not_log_data_endpoints: list[str] = []


class ReusePortWSGIServer(wsgi.WSGIServer):
    @staticmethod
    def prepare_socket(
        bind_addr: BindAddr,
        family: int,
        type_: int,
        proto: int,
        nodelay: bool,
        ssl_adapter: Adapter | None,
    ) -> socket.socket:
        """Set SO_REUSEPORT so several wazo-confd processes can bind the same
        port and let the kernel load-balance connections across them."""
        sock = wsgi.WSGIServer.prepare_socket(
            bind_addr, family, type_, proto, nodelay, ssl_adapter
        )
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        return sock


def get_bus_publisher():
    publisher = g.get('bus_publisher')
    if not publisher:
        publisher = g.bus_publisher = BusPublisher.from_reference()
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

        self._load_cors()
        self.server = None

    def _load_cors(self):
        cors_config = dict(self.config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(app, **cors_config)

    def run(self):
        if self.config['profile']:
            app.wsgi_app = ProfilerMiddleware(  # type: ignore[method-assign]
                app.wsgi_app, profile_dir=self.config['profile']
            )

        wsgi_app = ReverseProxied(ProxyFix(wsgi.WSGIPathInfoDispatcher({'/': app})))

        bind_addr = (self.config['listen'], self.config['port'])
        server_class = (
            ReusePortWSGIServer
            if self.config.get('reuse_port', False)
            else wsgi.WSGIServer
        )
        self.server = server_class(
            bind_addr=bind_addr,
            wsgi_app=wsgi_app,
            numthreads=self.config['max_threads'],
        )
        if self.config['certificate'] and self.config['private_key']:
            logger.warning(
                'Using service SSL configuration is deprecated. Please use NGINX instead.'
            )
            self.server.ssl_adapter = http_helpers.ssl_adapter(
                self.config['certificate'], self.config['private_key']
            )
        logger.debug(
            'WSGIServer starting... uid: %s, listen: %s:%s',
            os.getuid(),
            bind_addr[0],
            bind_addr[1],
        )
        for route in http_helpers.list_routes(app):
            logger.debug(route)

        self.server.start()

    def stop(self):
        if self.server:
            self.server.stop()
