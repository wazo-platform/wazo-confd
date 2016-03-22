# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2016 Avencall
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
from xivo.config_helper import read_config_file_hierarchy
from xivo.http_helpers import DEFAULT_CIPHERS
from xivo.xivo_logging import get_log_level_by_name


API_VERSION = '1.1'

DEFAULT_CONFIG = {
    'foreground': False,
    'debug': False,
    'profile': None,
    'user': 'www-data',
    'log_level': 'info',
    'config_file': '/etc/xivo-confd/config.yml',
    'extra_config_files': '/etc/xivo-confd/conf.d/',
    'log_filename': '/var/log/xivo-confd.log',
    'pid_filename': '/var/run/xivo-confd/xivo-confd.pid',
    'rest_api': {
        'http': {
            'enabled': True,
            'listen': '127.0.0.1',
            'port': 9487,
        },
        'https': {
            'enabled': True,
            'listen': '0.0.0.0',
            'port': 9486,
            'certificate': '/usr/share/xivo-certs/server.crt',
            'private_key': '/usr/share/xivo-certs/server.key',
            'ciphers': DEFAULT_CIPHERS,
        },
        'cors': {
            'enabled': True,
            'allow_headers': 'Content-Type',
        },
    },
    'auth': {
        'host': 'localhost',
        'port': 9497,
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
    'consul': {
        'scheme': 'https',
        'host': 'localhost',
        'port': 8500,
        'verify': '/usr/share/xivo-certs/server.crt',
    },
    'provd': {
    },
    'sysconfd': {
        'host': 'localhost',
        'port': '8668'
    },
    'default_plugins': [
        "api",
        "call_logs",
        "configuration",
        "cti_profiles",
        "extensions",
        "infos",
        "queue_members",
        "voicemails",
        "line_extension",
        "user_cti_profile",
        "user_line",
        "user_line_associated",
        "user_voicemail",
        "func_keys",
    ],
    'extra_plugins': [],
    'enabled_plugins': [
        'legacy_plugins',
        'user_plugin',
        'line_plugin',
        'endpoint_sip_plugin',
        'endpoint_sccp_plugin',
        'endpoint_custom_plugin',
        'line_sip_plugin',
        'device_plugin',
        'user_voicemail_plugin',
        'user_cti_profile_plugin',
        'user_line_plugin',
        'user_line_associated_plugin',
        'line_extension_plugin',
        'line_endpoint_plugin',
        'user_import_plugin',
        'line_device_plugin',
        'switchboard_plugin',
        'permission_plugin',
    ],
    'service_discovery': {
        'enabled': True,
        'advertise_address': 'localhost',
        'advertise_port': 9486,
        'advertise_address_interface': 'eth0',
        'refresh_interval': 25,
        'retry_interval': 2,
        'ttl_interval': 30,
        'extra_tags': [],
    },
}


def load(argv):
    cli_config = _parse_cli_args(argv)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, DEFAULT_CONFIG))
    reinterpreted_config = _get_reinterpreted_raw_values(ChainMap(cli_config, file_config, DEFAULT_CONFIG))
    return ChainMap(reinterpreted_config, cli_config, file_config, DEFAULT_CONFIG)


def _parse_cli_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config-file',
                        action='store',
                        help="The path where is the config file. Default: %(default)s")
    parser.add_argument('-d',
                        '--debug',
                        action='store_true',
                        help="Log debug messages. Overrides log_level. Default: %(default)s")
    parser.add_argument('-f',
                        '--foreground',
                        action='store_true',
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
                        help="The owner of the process.")
    parser.add_argument('-p',
                        '--profile',
                        help="Write profiling stats to directory (for debugging performance issues)",
                        action='store')
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.config_file:
        result['config_file'] = parsed_args.config_file
    if parsed_args.debug:
        result['debug'] = parsed_args.debug
    if parsed_args.profile:
        result['profile'] = parsed_args.profile
    if parsed_args.foreground:
        result['foreground'] = parsed_args.foreground
    if parsed_args.log_level:
        result['log_level'] = parsed_args.log_level
    if parsed_args.user:
        result['user'] = parsed_args.user

    return result


def _get_reinterpreted_raw_values(config):
    result = {}

    log_level = config.get('log_level')
    if log_level:
        result['log_level'] = get_log_level_by_name(log_level)

    return result
