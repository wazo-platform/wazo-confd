# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


import logging
import sys
import argparse
from xivo import daemonize
from flask_http_server import FlaskHttpServer


DAEMONNAME = 'xivo-recording'
DEBUG_MODE = False
LOGFILENAME = '/tmp/%s.log' % DAEMONNAME
PIDFILE = '/var/run/%s.pid' % DAEMONNAME

def main():
    parsed_args = _parse_args(sys.argv[1:])
    httpServer = FlaskHttpServer()
    httpServer.run()
    _init_logging(parsed_args.debug)
    if not parsed_args.debug:
        _daemonize()


def _init_logging(debug_mode):
    logger = logging.getLogger()
    formatter = logging.Formatter('%%(asctime)s %s[%%(process)d] (%%(levelname)s) (%%(name)s): %%(message)s'
                                  % DAEMONNAME)
    if debug_mode:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    logfilehandler = logging.FileHandler(LOGFILENAME)
    logfilehandler.setFormatter(formatter)
    logger.addHandler(logfilehandler)


def _daemonize():
    daemonize.daemonize()
    daemonize.lock_pidfile_or_die(PIDFILE)


def _parse_args(args):
    parser = _new_parser()
    return parser.parse_args(args)


def _new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    return parser


if __name__ == '__main__':
    main()
