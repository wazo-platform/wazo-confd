# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from datetime import timedelta
import logging
import os
from pprint import pformat
import urllib

from flask import Flask
from flask import g
from flask import request
from werkzeug.contrib.fixers import ProxyFix

from xivo_confd import flask_http_server
from xivo_confd.authentication.confd_auth import ConfdAuth
from xivo_confd.helpers.common import handle_error
from xivo_confd.helpers.mooltiparse import parser as mooltiparse_parser


logger = logging.getLogger(__name__)


class CoreRestApi(object):

    def __init__(self, config):
        self.config = config
        self.content_parser = mooltiparse_parser()

        self.app = Flask('xivo_confd')
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app)
        self.app.secret_key = os.urandom(24)
        self.app.permanent_session_lifetime = timedelta(minutes=5)
        self.auth = ConfdAuth()

        if config['debug']:
            logger.info("Debug mode enabled.")
            self.app.debug = True

        @self.app.before_request
        def log_requests():
            params = {
                'method': request.method,
                'url': urllib.unquote(request.url).decode('utf8')
            }
            if request.data:
                params.update({'data': request.data})
                logger.info("%(method)s %(url)s with data %(data)s ", params)
            else:
                logger.info("%(method)s %(url)s", params)

        @self.app.after_request
        def per_request_callbacks(response):
            for func in getattr(g, 'call_after_request', ()):
                response = func(response)
            params = {
                'statuscode': response.status_code,
                'method': request.method,
                'url': urllib.unquote(request.url).decode('utf8')
            }
            logger.info("%(method)s %(url)s %(statuscode)s", params)
            return response

        @self.app.errorhandler(Exception)
        def error_handler(error):
            return handle_error(error)

        flask_http_server.register_resources(self, config['default_plugins'])

        logger.debug('Loading extra plugins...')
        flask_http_server.register_resources(self, config['extra_plugins'])

    def blueprint(self, name):
        return self.app.blueprints[name]

    def register(self, blueprint):
        self.app.register_blueprint(blueprint)

    def run(self):
        bind_addr = (self.config['rest_api']['listen'], self.config['rest_api']['port'])

        from cherrypy import wsgiserver
        wsgi_app = wsgiserver.WSGIPathInfoDispatcher({'/': self.app})
        server = wsgiserver.CherryPyWSGIServer(bind_addr=bind_addr,
                                               wsgi_app=wsgi_app)

        logger.debug('WSGIServer starting... uid: %s, listen: %s:%s', os.getuid(), bind_addr[0], bind_addr[1])

        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
