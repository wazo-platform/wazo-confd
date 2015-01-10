# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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

import argparse

from xivo.chain_map import ChainMap
from xivo.config_helper import explicit_parsed_args
from xivo.config_helper import read_config_file_hierarchy

API_VERSION = '1.1'

DEFAULT_CONFIG = {
    'foreground': False,
    'debug': False,
    'user': 'www-data',
    'log_level': 'info',
    'config_file': '/etc/xivo-confd/config.yml',
    'extra_config_files': '/etc/xivo-confd/conf.d',
    'log_filename': '/var/log/xivo-confd.log',
    'pid_filename': '/var/run/xivo-confd/xivo-confd.pid',
    'rest_api': {
        'listen': '127.0.0.1',
        'port': 9487
    }
}


def load(argv):
    cli_config = _parse_cli_args(argv, DEFAULT_CONFIG)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, DEFAULT_CONFIG))

    return ChainMap(cli_config, file_config, DEFAULT_CONFIG)


def _parse_cli_args(argv, default_config):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config-file',
                        action='store',
                        help="The path where is the config file. Default: {}".format(default_config['config_file']))
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=None,
                        help="Log debug messages. Overrides log_level. Default: {}".format(default_config['debug']))
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        default=None,
                        help="Foreground, don't daemonize. Default: {}".format(default_config['foreground']))
    parser.add_argument('-u',
                        '--user',
                        action='store',
                        help="The owner of the process. Default: {}".format(default_config['user']))
    parsed_args = parser.parse_args(argv)
    return explicit_parsed_args(parsed_args)
