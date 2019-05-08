#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-confd',
    version='0.1',
    description='Wazo confd daemon',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),

    package_data={'xivo_confd.plugins': ['*/api.yml']},

    zip_safe=False,
    entry_points={
        'console_scripts': [
            'xivo-confd=xivo_confd.main:main',
        ],
        'xivo_confd.plugins': [
            'agent = xivo_confd.plugins.agent.plugin:Plugin',
            'agent_skill = xivo_confd.plugins.agent_skill.plugin:Plugin',
            'api = xivo_confd.plugins.api.plugin:Plugin',
            'application = xivo_confd.plugins.application.plugin:Plugin',
            'call_log = xivo_confd.plugins.call_log.plugin:Plugin',
            'call_filter = xivo_confd.plugins.call_filter.plugin:Plugin',
            'call_filter_fallback = xivo_confd.plugins.call_filter_fallback.plugin:Plugin',
            'call_filter_user = xivo_confd.plugins.call_filter_user.plugin:Plugin',
            'call_permission = xivo_confd.plugins.call_permission.plugin:Plugin',
            'call_pickup = xivo_confd.plugins.call_pickup.plugin:Plugin',
            'call_pickup_member = xivo_confd.plugins.call_pickup_member.plugin:Plugin',
            'confbridge = xivo_confd.plugins.confbridge.plugin:Plugin',
            'conference = xivo_confd.plugins.conference.plugin:Plugin',
            'conference_extension = xivo_confd.plugins.conference_extension.plugin:Plugin',
            'configuration = xivo_confd.plugins.configuration.plugin:Plugin',
            'context = xivo_confd.plugins.context.plugin:Plugin',
            'context_context = xivo_confd.plugins.context_context.plugin:Plugin',
            'cti_profile = xivo_confd.plugins.cti_profile.plugin:Plugin',
            'device = xivo_confd.plugins.device.plugin:Plugin',
            'dhcp = xivo_confd.plugins.dhcp.plugin:Plugin',
            'endpoint_custom = xivo_confd.plugins.endpoint_custom.plugin:Plugin',
            'endpoint_iax = xivo_confd.plugins.endpoint_iax.plugin:Plugin',
            'endpoint_sccp = xivo_confd.plugins.endpoint_sccp.plugin:Plugin',
            'endpoint_sip = xivo_confd.plugins.endpoint_sip.plugin:Plugin',
            'extension = xivo_confd.plugins.extension.plugin:Plugin',
            'extension_feature = xivo_confd.plugins.extension_feature.plugin:Plugin',
            'features = xivo_confd.plugins.features.plugin:Plugin',
            'func_key = xivo_confd.plugins.func_key.plugin:Plugin',
            'group = xivo_confd.plugins.group.plugin:Plugin',
            'group_call_permission = xivo_confd.plugins.group_call_permission.plugin:Plugin',
            'group_extension = xivo_confd.plugins.group_extension.plugin:Plugin',
            'group_fallback = xivo_confd.plugins.group_fallback.plugin:Plugin',
            'group_member_user = xivo_confd.plugins.group_member.plugin:Plugin',
            'group_schedule = xivo_confd.plugins.group_schedule.plugin:Plugin',
            'ha = xivo_confd.plugins.ha.plugin:Plugin',
            'hep = xivo_confd.plugins.hep.plugin:Plugin',
            'iax_callnumberlimits = xivo_confd.plugins.iax_callnumberlimits.plugin:Plugin',
            'iax_general = xivo_confd.plugins.iax_general.plugin:Plugin',
            'incall = xivo_confd.plugins.incall.plugin:Plugin',
            'incall_extension = xivo_confd.plugins.incall_extension.plugin:Plugin',
            'incall_schedule = xivo_confd.plugins.incall_schedule.plugin:Plugin',
            'info = xivo_confd.plugins.info.plugin:Plugin',
            'ivr = xivo_confd.plugins.ivr.plugin:Plugin',
            'line = xivo_confd.plugins.line.plugin:Plugin',
            'line_device = xivo_confd.plugins.line_device.plugin:Plugin',
            'line_endpoint = xivo_confd.plugins.line_endpoint.plugin:Plugin',
            'line_extension = xivo_confd.plugins.line_extension.plugin:Plugin',
            'line_sip = xivo_confd.plugins.line_sip.plugin:Plugin',
            'moh = xivo_confd.plugins.moh.plugin:Plugin',
            'outcall = xivo_confd.plugins.outcall.plugin:Plugin',
            'outcall_call_permission = xivo_confd.plugins.outcall_call_permission.plugin:Plugin',
            'outcall_extension = xivo_confd.plugins.outcall_extension.plugin:Plugin',
            'outcall_schedule = xivo_confd.plugins.outcall_schedule.plugin:Plugin',
            'outcall_trunk = xivo_confd.plugins.outcall_trunk.plugin:Plugin',
            'paging = xivo_confd.plugins.paging.plugin:Plugin',
            'paging_user = xivo_confd.plugins.paging_user.plugin:Plugin',
            'parking_lot = xivo_confd.plugins.parking_lot.plugin:Plugin',
            'parking_lot_extension = xivo_confd.plugins.parking_lot_extension.plugin:Plugin',
            'provisioning_networking = xivo_confd.plugins.provisioning_networking.plugin:Plugin',
            'queue = xivo_confd.plugins.queue.plugin:Plugin',
            'queue_extension = xivo_confd.plugins.queue_extension.plugin:Plugin',
            'queue_fallback = xivo_confd.plugins.queue_fallback.plugin:Plugin',
            'queue_general = xivo_confd.plugins.queue_general.plugin:Plugin',
            'queue_member = xivo_confd.plugins.queue_member.plugin:Plugin',
            'queue_schedule = xivo_confd.plugins.queue_schedule.plugin:Plugin',
            'rtp = xivo_confd.plugins.rtp.plugin:Plugin',
            'register_iax = xivo_confd.plugins.register_iax.plugin:Plugin',
            'register_sip = xivo_confd.plugins.register_sip.plugin:Plugin',
            'schedule = xivo_confd.plugins.schedule.plugin:Plugin',
            'sccp_general = xivo_confd.plugins.sccp_general.plugin:Plugin',
            'sip_general = xivo_confd.plugins.sip_general.plugin:Plugin',
            'skill = xivo_confd.plugins.skill.plugin:Plugin',
            'skill_rule = xivo_confd.plugins.skill_rule.plugin:Plugin',
            'sound = xivo_confd.plugins.sound.plugin:Plugin',
            'sound_language = xivo_confd.plugins.sound_language.plugin:Plugin',
            'switchboard = xivo_confd.plugins.switchboard.plugin:Plugin',
            'switchboard_member = xivo_confd.plugins.switchboard_member.plugin:Plugin',
            'timezone = xivo_confd.plugins.timezone.plugin:Plugin',
            'trunk = xivo_confd.plugins.trunk.plugin:Plugin',
            'trunk_endpoint = xivo_confd.plugins.trunk_endpoint.plugin:Plugin',
            'trunk_register = xivo_confd.plugins.trunk_register.plugin:Plugin',
            'user = xivo_confd.plugins.user.plugin:Plugin',
            'user_agent = xivo_confd.plugins.user_agent.plugin:Plugin',
            'user_call_permission = xivo_confd.plugins.user_call_permission.plugin:Plugin',
            'user_cti_profile = xivo_confd.plugins.user_cti_profile.plugin:Plugin',
            'user_fallback = xivo_confd.plugins.user_fallback.plugin:Plugin',
            'user_group = xivo_confd.plugins.user_group.plugin:Plugin',
            'user_import = xivo_confd.plugins.user_import.plugin:Plugin',
            'user_line = xivo_confd.plugins.user_line.plugin:Plugin',
            'user_line_associated = xivo_confd.plugins.user_line_associated.plugin:Plugin',
            'user_schedule = xivo_confd.plugins.user_schedule.plugin:Plugin',
            'user_voicemail = xivo_confd.plugins.user_voicemail.plugin:Plugin',
            'voicemail = xivo_confd.plugins.voicemail.plugin:Plugin',
            'voicemail_general = xivo_confd.plugins.voicemail_general.plugin:Plugin',
            'voicemail_zonemessages = xivo_confd.plugins.voicemail_zonemessages.plugin:Plugin',
            'wizard = xivo_confd.plugins.wizard.plugin:Plugin',
        ]
    }
)
