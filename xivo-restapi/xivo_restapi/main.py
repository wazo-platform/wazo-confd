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

import argparse
import logging

from xivo import daemonize
from xivo_restapi import flask_http_server
from xivo_restapi import config

DAEMONNAME = 'xivo-restapid'
LOGFILENAME = '/var/log/%s.log' % DAEMONNAME
PIDFILE = '/var/run/%s.pid' % DAEMONNAME

logger = logging.getLogger(__name__)


def main():
    parsed_args = _parse_args()

    _init_logging(parsed_args)

    if parsed_args.debug:
        logger.info("Debug mode enabled.")
        config.DEBUG = True
        flask_http_server.app.debug = True

    flask_http_server.register_blueprints_v1_0()
    flask_http_server.register_blueprints_v1_1()

    if parsed_args.dev_mode:
        logger.info("Starting xivo-restapid in dev mode.")
        config.HOST = parsed_args.listen_addr
        config.PORT = parsed_args.listen_port
        logger.info("Running on %s:%s", config.HOST, config.PORT)
        flask_http_server.app.run(host=config.HOST, port=config.PORT)
    else:
        from flup.server.fcgi import WSGIServer

        if parsed_args.foreground:
            logger.info("Starting xivo-restapid in foreground mode.")
        else:
            logger.info("Starting xivo-restapid in standard mode.")
            _daemonize()

        WSGIServer(flask_http_server.app,
                   bindAddress='/var/www/restws-fcgi.sock',
                   multithreaded=False,
                   multiprocess=True,
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
                        help="Listen on address <listen_addr> instead of %(default)s")
    parser.add_argument("--listen-port",
                        type=_port_number,
                        default=50050,
                        help="Listen on port <listen_port> instead of %(default)s")
    return parser.parse_args()


def _port_number(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError('%r is not a valid port number' % value)
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError('%r is not a valid port number' % value)
    return port


def _init_logging(parsed_args):
    formatter = logging.Formatter('%%(asctime)s %s[%%(process)d] (%%(levelname)s) (%%(name)s): %%(message)s'
                                  % DAEMONNAME)
    _init_data_access_logger(formatter)
    _init_root_logger(formatter, parsed_args)


def _init_data_access_logger(formatter):
    handler = logging.FileHandler(config.DATA_ACCESS_LOGFILENAME)
    handler.setFormatter(formatter)

    data_access_logger = logging.getLogger(config.DATA_ACCESS_LOGGERNAME)
    data_access_logger.addHandler(handler)
    data_access_logger.setLevel(logging.INFO)


def _init_root_logger(formatter, parsed_args):
    handler = logging.FileHandler(LOGFILENAME)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if parsed_args.foreground or parsed_args.dev_mode:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    if parsed_args.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


def _daemonize():
    daemonize.daemonize()
    daemonize.lock_pidfile_or_die(PIDFILE)


if __name__ == '__main__':
    main()
