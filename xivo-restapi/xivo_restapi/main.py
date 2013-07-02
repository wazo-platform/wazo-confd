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

    _init_logging(parsed_args.debug)

    flask_http_server.register_blueprints()
    if parsed_args.dev_mode:
        flask_http_server.FlaskHttpServer().run()
    else:
        from flup.server.fcgi import WSGIServer

        if parsed_args.debug:
            logger.info("Starting xivo-restapid in debug mode.")
        else:
            _daemonize()
            logger.info("Starting xivo-restapid in standard mode.")
        WSGIServer(flask_http_server.app, bindAddress='/var/www/restws-fcgi.sock',
                   multithreaded=False, multiprocess=True, debug=False).run()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--dev_mode', action='store_true')
    return parser.parse_args()


def _init_logging(debug_mode):
    formatter = logging.Formatter('%%(asctime)s %s[%%(process)d] (%%(levelname)s) (%%(name)s): %%(message)s'
                                  % DAEMONNAME)
    _init_data_access_logger(formatter)
    _init_root_logger(formatter, debug_mode)


def _init_data_access_logger(formatter):
    handler = logging.FileHandler(config.DATA_ACCESS_LOGFILENAME)
    handler.setFormatter(formatter)

    data_access_logger = logging.getLogger(config.DATA_ACCESS_LOGGERNAME)
    data_access_logger.addHandler(handler)
    data_access_logger.setLevel(logging.INFO)


def _init_root_logger(formatter, debug_mode):
    handler = logging.FileHandler(LOGFILENAME)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if debug_mode:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
        config.DEBUG = True
    else:
        root_logger.setLevel(logging.INFO)


def _daemonize():
    daemonize.daemonize()
    daemonize.lock_pidfile_or_die(PIDFILE)


if __name__ == '__main__':
    main()
