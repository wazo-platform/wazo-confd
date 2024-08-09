# Copyright 2020-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging

from wazo import xivo_logging
from wazo.chain_map import ChainMap
from wazo.config_helper import read_config_file_hierarchy
from xivo_dao import init_db_from_config
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.pjsip_transport import dao as transport_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.moh import dao as moh_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.tenant import dao as tenant_resources_dao
from xivo_dao import tenant_dao
from wazo_auth_client import Client as AuthClient

from wazo_confd._sysconfd import SysconfdPublisher
from wazo_confd.config import DEFAULT_CONFIG, _load_key_file
from wazo_confd.plugins.event_handlers.service import DefaultSIPTemplateService

logger = logging.getLogger('wazo-confd-sync-db')


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Log debug messages",
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Only print warnings and errors',
    )
    parsed_args = parser.parse_args()
    result = {'log_level': logging.INFO}
    if parsed_args.quiet:
        result['log_level'] = logging.WARNING
    elif parsed_args.debug:
        result['log_level'] = logging.DEBUG
    return result


def load_config():
    file_config = read_config_file_hierarchy(ChainMap(DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(file_config, DEFAULT_CONFIG))
    return ChainMap(service_key, file_config, DEFAULT_CONFIG)


def main():
    cli_args = parse_cli_args()
    config = load_config()

    xivo_logging.setup_logging('/dev/null', log_level=cli_args['log_level'])
    xivo_logging.silence_loggers(['stevedore.extension'], logging.WARNING)

    token = AuthClient(**config['auth']).token.new(expiration=300)['token']

    del config['auth']['username']
    del config['auth']['password']
    tenants = AuthClient(token=token, **config['auth']).tenants.list()['items']
    auth_tenants = set(tenant['uuid'] for tenant in tenants)
    auth_tenant_slugs = {tenant['uuid']: tenant['slug'] for tenant in tenants}
    logger.debug('wazo-auth tenants: %s', auth_tenants)

    sysconfd = SysconfdPublisher.from_config(config)

    init_db_from_config(config)
    default_sip_template_service = DefaultSIPTemplateService(
        sip_dao,
        transport_dao,
    )

    with session_scope() as session:
        confd_tenants = set()
        confd_tenant_without_slugs = set()
        for tenant in session.query(Tenant).all():
            confd_tenants.add(tenant.uuid)
            if not tenant.slug:
                confd_tenant_without_slugs.add(tenant.uuid)
        logger.debug('wazo-confd tenants: %s', confd_tenants)
        logger.debug('wazo-auth tenants: %s', auth_tenants)

        removed_tenants = confd_tenants - auth_tenants
        for tenant_uuid in removed_tenants:
            remove_tenant(tenant_uuid, sysconfd)

    with session_scope() as session:
        for tenant_uuid in auth_tenants:
            tenant = tenant_dao.find_or_create_tenant(tenant_uuid)
            default_sip_template_service.generate_sip_templates(tenant)

        for tenant_uuid in confd_tenant_without_slugs:
            slug = auth_tenant_slugs.get(tenant_uuid)
            if not slug:
                continue
            tenant = tenant_dao.find_or_create_tenant(tenant_uuid)
            tenant.slug = slug
            session.flush()


def remove_tenant(tenant_uuid, sysconfd):
    logger.debug('Removing tenant: %s', tenant_uuid)
    with session_scope():
        logger.debug('Retrieving contexts for tenant: %s', tenant_uuid)
        contexts = context_dao.search(tenant_uuids=[tenant_uuid])
        for context in contexts.items:
            logger.debug(
                'Deleting voicemails for tenant: %s, context: %s',
                tenant_uuid,
                context.name,
            )
            sysconfd.delete_voicemails(context.name)

        logger.debug('Retrieving all moh for tenant: %s', tenant_uuid)
        moh_list = moh_dao.search(tenant_uuids=[tenant_uuid])
        for moh in moh_list.items:
            logger.debug(
                'Deleting moh directory for tenant: %s, moh: %s',
                tenant_uuid,
                moh.name,
            )
            sysconfd.delete_moh(moh.name)

        logger.debug('Deleting all queues for tenant: %s', tenant_uuid)
        queues_list = queue_dao.search(tenant_uuids=[tenant_uuid])
        for queue in queues_list.items:
            queue_dao.delete(queue)

        logger.debug('Deleting all groups for tenant: %s', tenant_uuid)
        groups_list = group_dao.search(tenant_uuids=[tenant_uuid])
        for group in groups_list.items:
            group_dao.delete(group)

        tenant = tenant_resources_dao.get(tenant_uuid)
        tenant_resources_dao.delete(tenant)
    sysconfd.flush()


if __name__ == '__main__':
    main()
