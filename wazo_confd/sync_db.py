# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy

from wazo_auth_client import Client as AuthClient
from wazo_confd.config import DEFAULT_CONFIG, _load_key_file

logger = logging.getLogger(__name__)


def _parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Only print warnings and errors',
    )
    parsed_args = parser.parse_args()
    result = {}
    if parsed_args.quiet:
        result['sync_db'] = {'quiet': parsed_args.quiet}
    return result


def load_config():
    cli_config = _parse_cli_args()
    file_config = read_config_file_hierarchy(ChainMap(cli_config, DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(cli_config, file_config, DEFAULT_CONFIG))
    return ChainMap(cli_config, service_key, file_config, DEFAULT_CONFIG)


def main():
    config = load_config()

    if config.get('quiet'):
        logger.setLevel(logging.WARNING)

    token = AuthClient(**config['auth']).token.new(expiration=300)['token']

    del config['auth']['username']
    del config['auth']['password']
    tenants = AuthClient(token=token, **config['auth']).tenants.list()['items']
    for tenant in tenants:
        print(tenant)
