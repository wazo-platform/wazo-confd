# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo_dao import init_db_from_config
from xivo_dao.alchemy.tenant import Tenant
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao import tenant_dao
from wazo_auth_client import Client as AuthClient

from wazo_confd.config import DEFAULT_CONFIG, _load_key_file

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
            generate_sip_templates(tenant)


def remove_tenant(tenant_uuid):
    for user in user_dao.find_all_by(tenant_uuid=tenant_uuid):
        logger.debug('Removing user: %s', user.uuid)
        user_dao.delete(user)

    # FIXME(fblackburn):
    # * Add all other resources related to tenant_uuid
    # * Reset device to autoprov


def create_or_merge_sip_template(template_config, existing_template_uuid):
    if not existing_template_uuid:
        logger.info(
            'Creating "%s" SIPEndpointTemplate for tenant: %s',
            template_config['label'],
            template_config['tenant_uuid'],
        )
        template = EndpointSIP(**template_config)
        sip_dao.create(template)
        return template

    logger.info(
        'Resetting "%s" SIPEndpointTemplate for tenant: %s',
        template_config['label'],
        template_config['tenant_uuid'],
    )
    # NOTE(fblackburn): Allow to reset default values without breaking foreign key
    template = sip_dao.get(existing_template_uuid, template=True)
    for key, value in template_config.items():
        setattr(template, key, value)
    sip_dao.edit(template)

    return template


def generate_sip_templates(tenant):
    # TODO should be in common with event

    if tenant.sip_templates_generated:
        logger.debug('SIPEndpointTemplate already generated for tenant: %s', tenant.uuid)
        return

    transport_udp = transport_dao.find_by(name='transport-udp')
    transport_wss = transport_dao.find_by(name='transport-wss')

    global_config = {
        'label': 'global',
        'template': True,
        'tenant_uuid': tenant.uuid,
        'asterisk_id': None,
        'transport': transport_udp,
        'aor_section_options': [
            ['maximum_expiration', '3600'],
            ['default_expiration', '120'],
            ['minimum_expiration', '60'],
            ['qualify_frequency', '60'],
        ],
        'auth_section_options': [],
        'endpoint_section_options': [
            ['rtp_timeout', '7200'],
            ['allow_transfer', 'yes'],
            ['use_ptime', 'yes'],
            ['callerid', 'wazo'],
            ['direct_media', 'no'],
            ['dtmf_mode', 'rfc4733'],
            ['language', 'en_US'],
            ['inband_progress', 'no'],
            ['rtp_timeout_hold', '0'],
            ['timers_sess_expires', '600'],
            ['timers_min_se', '90'],
            ['trust_id_inbound', 'no'],
            ['allow_subscribe', 'yes'],
        ],
        'registration_section_options': [],
        'registration_outbound_auth_section_options': [],
        'identify_section_options': [],
        'outbound_auth_section_options': [],
        'templates': [],
    }
    global_template = create_or_merge_sip_template(
        global_config, tenant.global_sip_template_uuid,
    )

    webrtc_config = {
        'label': 'webrtc',
        'template': True,
        'tenant_uuid': tenant.uuid,
        'transport': transport_wss,
        'asterisk_id': None,
        'aor_section_options': [],
        'auth_section_options': [],
        'endpoint_section_options': [
            ['webrtc', 'yes'],
            ['dtls_auto_generate_cert', 'yes'],
            ['allow', '!all,opus,g722,alaw,ulaw,vp9,vp8,h264'],
        ],
        'registration_section_options': [],
        'registration_outbound_auth_section_options': [],
        'identify_section_options': [],
        'outbound_auth_section_options': [],
        'templates': [global_template],
    }
    webrtc_template = create_or_merge_sip_template(
        webrtc_config, tenant.webrtc_sip_template_uuid,
    )

    global_trunk_config = {
        'label': 'global_trunk',
        'template': True,
        'tenant_uuid': tenant.uuid,
        'transport': None,
        'asterisk_id': None,
        'aor_section_options': [],
        'auth_section_options': [],
        'endpoint_section_options': [],
        'registration_section_options': [
            ['forbidden_retry_interval', '30'],
            ['retry_interval', '20'],
            ['max_retries', '10000'],
            ['auth_rejection_permanent', 'no'],
            ['fatal_retry_interval', '30'],
        ],
        'registration_outbound_auth_section_options': [],
        'identify_section_options': [],
        'outbound_auth_section_options': [],
        'templates': [global_template],
    }
    global_trunk_template = create_or_merge_sip_template(
        global_trunk_config, tenant.global_trunk_sip_template_uuid,
    )

    twilio_trunk_config = {
        'label': 'twilio_trunk',
        'template': True,
        'tenant_uuid': tenant.uuid,
        'transport': None,
        'asterisk_id': None,
        'aor_section_options': [],
        'auth_section_options': [],
        'endpoint_section_options': [],
        'registration_section_options': [],
        'registration_outbound_auth_section_options': [],
        'identify_section_options': [
            ['match', '54.172.60.0'],
            ['match', '54.172.60.3'],
            ['match', '54.172.60.2'],
            ['match', '54.172.60.1'],
            ['match', '177.71.206.195'],
            ['match', '177.71.206.194'],
            ['match', '177.71.206.193'],
            ['match', '177.71.206.192'],
            ['match', '54.252.254.67'],
            ['match', '54.252.254.66'],
            ['match', '54.252.254.65'],
            ['match', '54.252.254.64'],
            ['match', '54.169.127.131'],
            ['match', '54.169.127.130'],
            ['match', '54.169.127.129'],
            ['match', '54.169.127.128'],
            ['match', '54.65.63.195'],
            ['match', '54.65.63.194'],
            ['match', '54.65.63.193'],
            ['match', '54.65.63.192'],
            ['match', '35.156.191.131'],
            ['match', '35.156.191.130'],
            ['match', '35.156.191.129'],
            ['match', '35.156.191.128'],
            ['match', '54.171.127.195'],
            ['match', '54.171.127.194'],
            ['match', '54.171.127.193'],
            ['match', '54.171.127.192'],
            ['match', '54.244.51.3'],
            ['match', '54.244.51.2'],
            ['match', '54.244.51.1'],
            ['match', '54.244.51.0'],
        ],
        'outbound_auth_section_options': [],
        'templates': [global_trunk_template],
    }
    twilio_trunk_template = create_or_merge_sip_template(
        twilio_trunk_config, tenant.twilio_trunk_sip_template_uuid,
    )

    tenant.global_sip_template_uuid = global_template.uuid
    tenant.webrtc_sip_template_uuid = webrtc_template.uuid
    tenant.global_trunk_sip_template_uuid = global_trunk_template.uuid
    tenant.twilio_trunk_sip_template_uuid = twilio_trunk_template.uuid
    tenant.sip_templates_generated = True
