# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

import netifaces
import random
import re
import socket

from xivo_confd import sysconfd
from xivo_confd.application import commit_database
from xivo_confd.plugins.wizard.notifier import build_notifier
from xivo_confd.plugins.wizard.validator import build_validator
from xivo_confd.database import wizard as wizard_db

USERNAME_VALUES = '2346789bcdfghjkmnpqrtvwxyzBCDFGHJKLMNPQRTVWXYZ'
NAMESERVER_REGEX = '^nameserver (.*)'


class WizardService(object):

    def __init__(self, validator, notifier, infos_dao, provd_client, sysconfd):
        self.validator = validator
        self.notifier = notifier
        self.infos_dao = infos_dao
        self.provd_client = provd_client
        self.sysconfd = sysconfd

    def get(self):
        return wizard_db.get_xivo_configured()

    def create(self, wizard):
        self.validator.validate_create(wizard)
        autoprov_username = self._generate_autoprov_username()
        wizard_db.create(wizard, autoprov_username)
        commit_database()
        self._send_sysconfd_cmd(wizard['network']['hostname'],
                                wizard['network']['domain'],
                                wizard['network']['nameservers'])
        self._initialize_provd(wizard['network']['ip_address'], autoprov_username)

        wizard_db.set_xivo_configured()
        self.notifier.created()
        wizard['xivo_uuid'] = self.infos_dao.get().uuid
        return wizard

    def _send_sysconfd_cmd(self, hostname, domain, nameserver):
        self.sysconfd.xivo_service_enable()
        self.sysconfd.flush()
        self.sysconfd.xivo_service_start()
        self.sysconfd.flush()
        self.sysconfd.set_hosts(hostname, domain)
        self.sysconfd.set_resolvconf(nameserver, domain)
        self.sysconfd.commonconf_generate()
        self.sysconfd.flush()
        self.sysconfd.commonconf_apply()
        self.sysconfd.flush()

    def _initialize_provd(self, address, autoprov_username):
        default_config = {'X_type': 'registrar',
                          'id': 'default',
                          'deletable': False,
                          'displayname': 'local',
                          'parent_ids': [],
                          'raw_config': {'X_key': 'xivo'},
                          'proxy_main': address,
                          'registrar_main': address}
        base_config = {'X_type': 'internal',
                       'id': 'base',
                       'deletable': False,
                       'parent_ids': [],
                       'raw_config': {'ntp_enabled': True,
                                      'ntp_ip': address,
                                      'X_xivo_phonebook_ip': address}}
        device_config = {u'X_type': u'device',
                         u'deletable': False,
                         u'id': u'defaultconfigdevice',
                         u'label': u'Default config device',
                         u'parent_ids': [],
                         u'raw_config': {u'ntp_enabled': True,
                                         u'ntp_ip': address,
                                         u'sip_dtmf_mode': u'RTP-out-of-band'}}
        autoprov_config = {u'X_type': u'internal',
                           u'deletable': False,
                           u'id': u'autoprov',
                           u'parent_ids': [u'base', u'defaultconfigdevice'],
                           u'raw_config': {u'sccp_call_managers': {u'1': {u'ip': address}},
                                           u'sip_lines': {u'1': {u'display_name': u'Autoprov',
                                                                 u'number': u'autoprov',
                                                                 u'password': u'autoprov',
                                                                 u'proxy_ip': address,
                                                                 u'registrar_ip': address,
                                                                 u'username': autoprov_username}}},
                           u'role': u'autocreate'}

        self.provd_client.config_manager().add(base_config)
        self.provd_client.config_manager().add(default_config)
        self.provd_client.config_manager().add(device_config)
        self.provd_client.config_manager().add(autoprov_config)

    def _generate_autoprov_username(self):
        suffix = ''.join(random.choice(USERNAME_VALUES) for _ in range(8))
        return 'ap{}'.format(suffix)

    def get_interfaces(self):
        result = []
        candidate_interfaces = (interface for interface in netifaces.interfaces()
                                if interface != 'lo')
        for interface in candidate_interfaces:
            addresses_ipv4 = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
            for address in addresses_ipv4:
                result.append({'ip_address': address.get('addr'),
                               'netmask': address.get('netmask'),
                               'interface': interface})
        return result

    def get_gateways(self):
        gateways = []
        for gateway in netifaces.gateways().get(netifaces.AF_INET, []):
            gateways.append({'gateway': gateway[0],
                             'interface': gateway[1]})
        return gateways

    def get_nameservers(self):
        nameserver_regex = re.compile(NAMESERVER_REGEX)
        nameservers = []
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f.readlines():
                    nameserver = re.match(nameserver_regex, line)
                    if nameserver:
                        nameservers.append(nameserver.group(1))
        except IOError:
            pass

        return nameservers

    def get_timezone(self):
        try:
            with open('/etc/timezone', 'r') as f:
                return f.readline().strip()
        except IOError:
            return None

    def get_hostname(self):
        return self._hostname_without_domain()

    def get_domain(self):
        return self._fqdn_without_hostname()

    def _hostname_without_domain(self):
        hostname = socket.gethostname().split('.', 1)
        return hostname[0]

    def _fqdn_without_hostname(self):
        fqdn = socket.getfqdn().split('.', 1)
        if len(fqdn) == 2:
            return fqdn[1]
        return None


def build_service(provd_client, infos_dao):
    return WizardService(build_validator(),
                         build_notifier(),
                         infos_dao,
                         provd_client,
                         sysconfd)
