# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

import os

from xivo_provd_client import new_provisioning_client


class ProvdHelper(object):

    DEFAULT_CONFIGS = [{u'X_type': u'registrar',
                        u'deletable': False,
                        u'displayname': u'local',
                        u'id': u'default',
                        u'parent_ids': [],
                        u'proxy_main': u'127.0.0.1',
                        u'raw_config': {u'X_key': u'xivo'},
                        u'registrar_main': u'127.0.0.1'},
                       {u'X_type': u'internal',
                        u'deletable': False,
                        u'id': u'autoprov',
                        u'parent_ids': [u'base', u'defaultconfigdevice'],
                        u'raw_config': {u'sccp_call_managers': {u'1': {u'ip': u'127.0.0.1'}},
                                        u'sip_lines': {u'1': {u'display_name': u'Autoprov',
                                                              u'number': u'autoprov',
                                                              u'password': u'autoprov',
                                                              u'proxy_ip': u'127.0.0.1',
                                                              u'registrar_ip': u'127.0.0.1',
                                                              u'username': u'apmy3dCQDw'}}},
                        u'role': u'autocreate'},
                       {u'X_type': u'internal',
                        u'deletable': False,
                        u'id': u'base',
                        u'parent_ids': [],
                        u'raw_config': {u'X_xivo_phonebook_ip': u'127.0.0.1',
                                        u'ntp_enabled': True,
                                        u'ntp_ip': u'127.0.0.1'}},
                       {u'X_type': u'device',
                        u'deletable': False,
                        u'id': u'defaultconfigdevice',
                        u'label': u'Default config device',
                        u'parent_ids': [],
                        u'raw_config': {u'ntp_enabled': True, u'ntp_ip': u'127.0.0.1'}}]

    def __init__(self, client):
        self.client = client

    @property
    def configs(self):
        return self.client.config_manager()

    @property
    def devices(self):
        return self.client.device_manager()

    def reset(self):
        self.clean_devices()
        self.clean_configs()
        self.add_default_configs()

    def clean_devices(self):
        for device in self.devices.find():
            self.devices.remove(device['id'])

    def clean_configs(self):
        for config in self.configs.find():
            self.configs.remove(config['id'])

    def add_default_configs(self):
        for config in self.DEFAULT_CONFIGS:
            self.configs.add(config)


def create_helper():
    host = os.environ.get('PROVD_HOST', 'localhost')
    port = os.environ.get('PROVD_PORT', 8666)
    url = "http://{host}:{port}/provd".format(host=host, port=port)
    client = new_provisioning_client(url)
    return ProvdHelper(client)
