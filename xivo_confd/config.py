# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo.config_helper import parse_config_file
from xivo.xivo_logging import get_log_level_by_name

API_VERSION = '1.1'

DEFAULT_CONFIG = {
    'foreground': False,
    'debug': False,
    'user': 'www-data',
    'log_level': 'info',
    'config_file': '/etc/xivo-confd/config.yml',
    'log_filename': '/var/log/xivo-confd.log',
    'pid_filename': '/var/run/xivo-confd/xivo-confd.pid',
    'rest_api': {
        'listen': '127.0.0.1',
        'port': 9487
    },
    'bus': {
        'username': 'guest',
        'password': 'guest',
        'host': 'localhost',
        'port': 5672,
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
        'exchange_durable': True,
    },
    'default_plugins': [
        "call_logs",
        "configuration",
        "cti_profiles",
        "devices",
        "extensions",
        "infos",
        "lines",
        "queue_members",
        "users",
        "voicemails",
        "line_extension",
        "line_extension_collection",
        "user_cti_profile",
        "user_line",
        "user_voicemail",
    ],
    'extra_plugins': [],
}


def load(argv):
    config = dict(DEFAULT_CONFIG)

    config.update(_parse_cli_args(argv, DEFAULT_CONFIG))
    config.update(parse_config_file(config['config_file']))
    _interpret_raw_values(config)

    return config


def _parse_cli_args(argv, default_config):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config-file',
                        action='store',
                        default=default_config['config_file'],
                        help="The path where is the config file. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        default=default_config['debug'],
                        help="Log debug messages. Overrides log_level. Default: %(default)s")
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
                        default=default_config['foreground'],
                        help="Foreground, don't daemonize. Default: %(default)s")
    parser.add_argument('-l',
                        '--log-level',
                        action='store',
                        default='INFO',
                        help="Logs messages with LOG_LEVEL details. Must be one of:\n"
                             "critical, error, warning, info, debug. Default: %(default)s")
    parser.add_argument('-u',
                        '--user',
                        action='store',
                        default=default_config['user'],
                        help="The owner of the process.")
    parsed_args = parser.parse_args(argv)
    return vars(parsed_args)


def _interpret_raw_values(config):
    config['log_level'] = get_log_level_by_name(config['log_level'])
