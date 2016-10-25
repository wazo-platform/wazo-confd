#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2016 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-confd',
    version='0.1',
    description='XIVO CONFD daemon',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://github.com/xivo-pbx/xivo-confd',
    license='GPLv3',
    packages=find_packages(),
    scripts=[
        'bin/xivo-confd'
    ],

    package_data={'xivo_confd.plugins': ['*/api.yml']},

    zip_safe=False,
    entry_points={
        'xivo_confd.plugins': [
            'plugin_list = xivo_confd.plugins.plugin_list:Plugin',
            'api_plugin = xivo_confd.plugins.api.plugin:Plugin',
            'call_log_plugin = xivo_confd.plugins.call_log.plugin:Plugin',
            'call_permission_plugin = xivo_confd.plugins.call_permission.plugin:Plugin',
            'configuration_plugin = xivo_confd.plugins.configuration.plugin:Plugin',
            'cti_profile_plugin = xivo_confd.plugins.cti_profile.plugin:Plugin',
            'device_plugin = xivo_confd.plugins.device.plugin:Plugin',
            'endpoint_custom_plugin = xivo_confd.plugins.endpoint_custom.plugin:Plugin',
            'endpoint_sccp_plugin = xivo_confd.plugins.endpoint_sccp.plugin:Plugin',
            'endpoint_sip_plugin = xivo_confd.plugins.endpoint_sip.plugin:Plugin',
            'entity_plugin = xivo_confd.plugins.entity.plugin:Plugin',
            'extension_plugin = xivo_confd.plugins.extension.plugin:Plugin',
            'func_key_plugin = xivo_confd.plugins.func_key.plugin:Plugin',
            'incall_extension_plugin = xivo_confd.plugins.incall_extension.plugin:Plugin',
            'incall_plugin = xivo_confd.plugins.incall.plugin:Plugin',
            'info_plugin = xivo_confd.plugins.info.plugin:Plugin',
            'ivr_plugin = xivo_confd.plugins.ivr.plugin:Plugin',
            'line_device_plugin = xivo_confd.plugins.line_device.plugin:Plugin',
            'line_endpoint_plugin = xivo_confd.plugins.line_endpoint.plugin:Plugin',
            'line_extension_plugin = xivo_confd.plugins.line_extension.plugin:Plugin',
            'line_plugin = xivo_confd.plugins.line.plugin:Plugin',
            'line_sip_plugin = xivo_confd.plugins.line_sip.plugin:Plugin',
            'outcall_extension_plugin = xivo_confd.plugins.outcall_extension.plugin:Plugin',
            'outcall_plugin = xivo_confd.plugins.outcall.plugin:Plugin',
            'outcall_trunk_plugin = xivo_confd.plugins.outcall_trunk.plugin:Plugin',
            'queue_member_plugin = xivo_confd.plugins.queue_member.plugin:Plugin',
            'sip_general_plugin = xivo_confd.plugins.sip_general.plugin:Plugin',
            'switchboard_plugin = xivo_confd.plugins.switchboard.plugin:Plugin',
            'trunk_endpoint_plugin = xivo_confd.plugins.trunk_endpoint.plugin:Plugin',
            'trunk_plugin = xivo_confd.plugins.trunk.plugin:Plugin',
            'user_agent_plugin = xivo_confd.plugins.user_agent.plugin:Plugin',
            'user_call_permission_plugin = xivo_confd.plugins.user_call_permission.plugin:Plugin',
            'user_cti_profile_plugin = xivo_confd.plugins.user_cti_profile.plugin:Plugin',
            'user_entity_plugin = xivo_confd.plugins.user_entity.plugin:Plugin',
            'user_import_plugin = xivo_confd.plugins.user_import.plugin:Plugin',
            'user_line_associated_plugin = xivo_confd.plugins.user_line_associated.plugin:Plugin',
            'user_line_plugin = xivo_confd.plugins.user_line.plugin:Plugin',
            'user_plugin = xivo_confd.plugins.user.plugin:Plugin',
            'user_voicemail_plugin = xivo_confd.plugins.user_voicemail.plugin:Plugin',
            'voicemail_plugin = xivo_confd.plugins.voicemail.plugin:Plugin',
            'wizard_plugin = xivo_confd.plugins.wizard.plugin:Plugin',
        ]
    }
)
