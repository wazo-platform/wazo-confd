# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import logging

import argparse

from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_confd import config
from xivo_confd import flask_http_server


DAEMONNAME = 'xivo-confd'
LOGFILENAME = '/var/log/{}.log'.format(DAEMONNAME)
PID_FILENAME = '/var/run/{daemon}/{daemon}.pid'.format(daemon=DAEMONNAME)
SOCKET_FILENAME = '/var/run/{daemon}/{daemon}.sock'.format(daemon=DAEMONNAME)

logger = logging.getLogger(__name__)


def main():
    parsed_args = _parse_args()

    setup_logging(LOGFILENAME, parsed_args.foreground, parsed_args.debug)

    if parsed_args.user:
        change_user(parsed_args.user)
    if parsed_args.debug:
        logger.info("Debug mode enabled.")
        flask_http_server.app.debug = True

    flask_http_server.register_blueprints_v1_1()

    if parsed_args.dev_mode:
        logger.info("Starting xivo-confd in dev mode.")
        config.HOST = parsed_args.listen_addr
        config.PORT = parsed_args.listen_port
        logger.info("Running on %s:%s", config.HOST, config.PORT)
        flask_http_server.app.run(host=config.HOST, port=config.PORT)
    else:
        from flup.server.fcgi import WSGIServer

        if parsed_args.foreground:
            logger.info("Starting xivo-confd in foreground mode.")
        else:
            logger.info("Starting xivo-confd in standard mode.")

        with pidfile_context(PID_FILENAME, parsed_args.foreground):
            WSGIServer(flask_http_server.app,
                       bindAddress=SOCKET_FILENAME,
                       multithreaded=True,
                       multiprocess=False,
                       debug=False).run()


def _parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f",
                       '--foreground',
                       action='store_true',
                       default=False,
                       help="Foreground, don't daemonize. Not use with <dev_mode>. Default: %(default)s")
    group.add_argument('--dev_mode',
                       action='store_true',
                       default=False,
                       help="Launch Flask in dev mode, not use wsgi. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=False,
                        help="Activate debug message. Default: %(default)s")
    parser.add_argument("--listen-addr",
                        default='0.0.0.0',
                        help="Listen on address <listen_addr>. Default: %(default)s")
    parser.add_argument("--listen-port",
                        type=_port_number,
                        default=9487,
                        help="Listen on port <listen_port>. Default: %(default)s")
    parser.add_argument('-u',
                        '--user',
                        default='www-data',
                        action='store',
                        help="The owner of the process. Default: %(default)s")
    return parser.parse_args()


def _port_number(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('%r is not a valid port number' % value)
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError('%r is not a valid port number' % value)
    return port


if __name__ == '__main__':
    main()
