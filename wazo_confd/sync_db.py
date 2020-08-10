# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo_dao import init_db_from_config
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao import tenant_dao
from wazo_auth_client import Client as AuthClient

from wazo_confd.config import DEFAULT_CONFIG, _load_key_file
from wazo_confd.plugins.event_handlers.service import DefaultSIPTemplateService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wazo-confd-sync-db')


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true', help="Log debug messages",
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true', help='Only print warnings and errors',
    )
    parsed_args = parser.parse_args()
    result = {}
    if parsed_args.quiet:
        logger.setLevel(logging.WARNING)
    elif parsed_args.debug:
        logger.setLevel(logging.DEBUG)
    return result


def load_config():
    file_config = read_config_file_hierarchy(ChainMap(DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(file_config, DEFAULT_CONFIG))
    return ChainMap(service_key, file_config, DEFAULT_CONFIG)


def main():
    parse_cli_args()
    config = load_config()

    token = AuthClient(**config['auth']).token.new(expiration=300)['token']

    del config['auth']['username']
    del config['auth']['password']
    tenants = AuthClient(token=token, **config['auth']).tenants.list()['items']
    auth_tenants = set(tenant['uuid'] for tenant in tenants)
    logger.debug('wazo-auth tenants: %s', auth_tenants)

    init_db_from_config(config)
    default_sip_template_service = DefaultSIPTemplateService(
        sip_dao, transport_dao,
    )

    with session_scope() as session:
        tenants = session.query(Tenant).all()
        confd_tenants = set(tenant.uuid for tenant in tenants)
        logger.debug('wazo-confd tenants: %s', confd_tenants)

        removed_tenants = confd_tenants - auth_tenants
        for tenant_uuid in removed_tenants:
            logger.info('Removing tenant: %s... (SKIP)', tenant_uuid)
            remove_tenant(tenant_uuid)

    with session_scope() as session:
        for tenant_uuid in auth_tenants:
            tenant = tenant_dao.find_or_create_tenant(tenant_uuid)
            default_sip_template_service.generate_sip_templates(tenant)


def remove_tenant(tenant_uuid):
    for user in user_dao.find_all_by(tenant_uuid=tenant_uuid):
        logger.debug('Removing user: %s', user.uuid)
        user_dao.delete(user)

    # FIXME(fblackburn):
    # * Add all other resources related to tenant_uuid
    # * Reset device to autoprov
