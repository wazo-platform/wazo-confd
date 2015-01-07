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
import urllib

from flask import Flask
from flask import request
from gevent.pywsgi import WSGIServer

from xivo_confd import flask_http_server
from xivo_confd.helpers.common import handle_error


logger = logging.getLogger(__name__)


class CoreRestApi(object):

    def __init__(self, config):
        self.config = config

        self.app = Flask('xivo_confd')
        self.app.secret_key = os.urandom(24)
        self.app.permanent_session_lifetime = timedelta(minutes=5)

        if config['debug']:
            logger.info("Debug mode enabled.")
            self.app.debug = True

        flask_http_server.register_blueprints_v1_1(self.app)

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

        @self.app.errorhandler(Exception)
        def error_handler(error):
            return handle_error(error)

    def run(self):
        environ = {
            'wsgi.multithread': True,
        }
        http_server = WSGIServer(listener=(self.config['rest_api']['listen'], self.config['rest_api']['port']),
                                 application=self.app,
                                 environ=environ)

        logger.debug('WSGIServer starting... uid: %s, listen: %s:%s',
                     os.getuid(),
                     self.config['rest_api']['listen'],
                     self.config['rest_api']['port'])

        http_server.serve_forever()
