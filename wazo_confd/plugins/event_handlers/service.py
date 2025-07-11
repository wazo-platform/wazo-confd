# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.alchemy.endpoint_sip import EndpointSIP

logger = logging.getLogger(__name__)


class DefaultSIPTemplateService:
    def __init__(self, sip_dao, transport_dao):
        self.sip_dao = sip_dao
        self.transport_dao = transport_dao

    def copy_slug(self, tenant, slug):
        tenant.slug = slug

    def create_or_merge_sip_template(self, template_config, existing_template_uuid):
        if not existing_template_uuid:
            logger.info(
                'Creating "%s" SIPEndpointTemplate for tenant: %s',
                template_config['label'],
                template_config['tenant_uuid'],
            )
            template = EndpointSIP(**template_config)
            self.sip_dao.create(template)
            return template

        logger.info(
            'Resetting "%s" SIPEndpointTemplate for tenant: %s',
            template_config['label'],
            template_config['tenant_uuid'],
        )
        # NOTE(fblackburn): Allow to reset default values without breaking foreign key
        template = self.sip_dao.get(existing_template_uuid, template=True)
        for key, value in template_config.items():
            setattr(template, key, value)
        self.sip_dao.edit(template)

        return template

    def generate_sip_templates(self, tenant):
        if tenant.sip_templates_generated:
            logger.debug(
                'SIPEndpointTemplate already generated for tenant: %s', tenant.uuid
            )
            return

        transport_udp = self.transport_dao.find_by(name='transport-udp')
        transport_wss = self.transport_dao.find_by(name='transport-wss')

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
                ['remove_existing', 'true'],
                ['max_contacts', '1'],
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
                ['allow', '!all,ulaw'],
                ['set_var', 'TIMEOUT(absolute)=36000'],
                ['set_var', 'DYNAMIC_FEATURES=togglerecord'],
                ['notify_early_inuse_ringing', 'yes'],
            ],
            'registration_section_options': [],
            'registration_outbound_auth_section_options': [],
            'identify_section_options': [],
            'outbound_auth_section_options': [],
            'templates': [],
        }
        global_template = self.create_or_merge_sip_template(
            global_config,
            tenant.global_sip_template_uuid,
        )

        webrtc_config = {
            'label': 'webrtc',
            'template': True,
            'tenant_uuid': tenant.uuid,
            'transport': transport_wss,
            'asterisk_id': None,
            'aor_section_options': [
                ['remove_existing', 'false'],
                ['max_contacts', '10'],
            ],
            'auth_section_options': [],
            'endpoint_section_options': [
                ['webrtc', 'yes'],
                ['dtls_auto_generate_cert', 'yes'],
                ['allow', '!all,opus,g722,alaw,ulaw,vp9,vp8,h264'],
                ['max_video_streams', '25'],
                ['max_audio_streams', '1'],
                ['timers', 'always'],
                ['timers_sess_expires', '300'],
                ['timers_min_se', '90'],
            ],
            'registration_section_options': [],
            'registration_outbound_auth_section_options': [],
            'identify_section_options': [],
            'outbound_auth_section_options': [],
            'templates': [global_template],
        }
        webrtc_template = self.create_or_merge_sip_template(
            webrtc_config,
            tenant.webrtc_sip_template_uuid,
        )

        meeting_guest_config = {
            'label': 'meeting_guest',
            'template': True,
            'tenant_uuid': tenant.uuid,
            'transport': None,
            'asterisk_id': None,
            'templates': [webrtc_template],
        }
        meeting_guest_template = self.create_or_merge_sip_template(
            meeting_guest_config,
            tenant.meeting_guest_sip_template_uuid,
        )

        registration_trunk_config = {
            'label': 'registration_trunk',
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
        registration_trunk_template = self.create_or_merge_sip_template(
            registration_trunk_config,
            tenant.registration_trunk_sip_template_uuid,
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
            'templates': [registration_trunk_template],
        }
        twilio_trunk_template = self.create_or_merge_sip_template(
            twilio_trunk_config,
            tenant.twilio_trunk_sip_template_uuid,
        )

        tenant.global_sip_template_uuid = global_template.uuid
        tenant.webrtc_sip_template_uuid = webrtc_template.uuid
        tenant.meeting_guest_sip_template_uuid = meeting_guest_template.uuid
        tenant.registration_trunk_sip_template_uuid = registration_trunk_template.uuid
        tenant.twilio_trunk_sip_template_uuid = twilio_trunk_template.uuid
        tenant.sip_templates_generated = True
