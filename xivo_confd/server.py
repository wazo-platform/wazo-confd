import logging
import cherrypy

from cherrypy import wsgiserver
from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
from cherrypy.process.servers import ServerAdapter
from cherrypy.wsgiserver import CherryPyWSGIServer

from werkzeug.contrib.fixers import ProxyFix

logger = logging.getLogger(__name__)


def run_server(app):
    http_config = app.config['rest_api']['http']
    https_config = app.config['rest_api']['https']

    app.wsgi_app = ProxyFix(app.wsgi_app)
    wsgi_app = wsgiserver.WSGIPathInfoDispatcher({'/': app})

    bind_addr_https = (https_config['host'], https_config['port'])

    cherrypy.server.unsubscribe()
    cherrypy.config.update({'environment': 'production'})

    if not (http_config['enabled'] and https_config['enabled']):
        logger.critical('No HTTP server enabled')
        exit()

    if https_config['enabled']:
        try:
            _check_file_readable(https_config['certificate'])
            _check_file_readable(https_config['private_key'])

            bind_addr_https = (https_config['host'], https_config['port'])
            ssl_adapter = BuiltinSSLAdapter(https_config['certificate'],
                                            https_config['private_key'])
            server_https = CherryPyWSGIServer(bind_addr=bind_addr_https,
                                              wsgi_app=wsgi_app)
            server_https.ssl_adapter = ssl_adapter
            ServerAdapter(cherrypy.engine, server_https).subscribe()

            logger.debug('HTTPS server starting on %s:%s', *bind_addr_https)

        except IOError as e:
            logger.warning("HTTPS server won't start: %s", e)
    else:
        logger.debug('HTTPS server is disabled')

    if http_config['enabled']:
        bind_addr_http = (http_config['host'], http_config['port'])
        server_http = CherryPyWSGIServer(bind_addr=bind_addr_http,
                                         wsgi_app=wsgi_app)
        ServerAdapter(cherrypy.engine, server_http).subscribe()

        logger.debug('HTTP server starting on %s:%s', *bind_addr_http)
    else:
        logger.debug('HTTP server is disabled')

    try:
        cherrypy.engine.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        cherrypy.engine.stop()


def _check_file_readable(file_path):
    with open(file_path, 'r'):
        pass
