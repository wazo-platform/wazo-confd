# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import logging
import cherrypy

from cherrypy.process.servers import ServerAdapter
from cheroot import wsgi
from werkzeug.contrib.profiler import ProfilerMiddleware
from werkzeug.contrib.fixers import ProxyFix
from xivo import http_helpers
from xivo.http_helpers import ReverseProxied

logger = logging.getLogger(__name__)


def run_server(app):
    http_config = app.config['rest_api']['http']
    https_config = app.config['rest_api']['https']

    cherrypy.engine.signal_handler.set_handler('SIGTERM', cherrypy.engine.exit)
    if app.config['profile']:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                          profile_dir=app.config['profile'])

    wsgi_app = ReverseProxied(ProxyFix(wsgi.WSGIPathInfoDispatcher({'/': app})))

    cherrypy.server.unsubscribe()
    cherrypy.config.update({'environment': 'production'})

    if not (http_config['enabled'] or https_config['enabled']):
        logger.critical('No HTTP/HTTPS server enabled')
        exit()

    if https_config['enabled']:
        try:
            bind_addr_https = (https_config['listen'], https_config['port'])
            server_https = wsgi.WSGIServer(bind_addr=bind_addr_https,
                                           wsgi_app=wsgi_app)
            server_https.ssl_adapter = http_helpers.ssl_adapter(https_config['certificate'],
                                                                https_config['private_key'])
            ServerAdapter(cherrypy.engine, server_https).subscribe()

            logger.debug('HTTPS server starting on %s:%s', *bind_addr_https)

        except IOError as e:
            logger.warning("HTTPS server won't start: %s", e)
    else:
        logger.debug('HTTPS server is disabled')

    if http_config['enabled']:
        bind_addr_http = (http_config['listen'], http_config['port'])
        server_http = wsgi.WSGIServer(bind_addr=bind_addr_http,
                                      wsgi_app=wsgi_app)
        ServerAdapter(cherrypy.engine, server_http).subscribe()

        logger.debug('HTTP server starting on %s:%s', *bind_addr_http)
    else:
        logger.debug('HTTP server is disabled')

    cherrypy.engine.start()
    cherrypy.engine.block()
