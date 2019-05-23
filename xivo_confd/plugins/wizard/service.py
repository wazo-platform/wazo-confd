# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import netifaces
import random
import re
import socket
import string

from os import urandom
from xivo_dao.helpers.db_utils import session_scope

from xivo_confd import sysconfd
from xivo_confd.database import wizard as wizard_db

from .notifier import build_notifier
from .validator import build_validator

USERNAME_VALUES = '2346789bcdfghjkmnpqrtvwxyzBCDFGHJKLMNPQRTVWXYZ'
NAMESERVER_REGEX = r'^nameserver (.*)'
DEFAULT_ADMIN_POLICY = 'wazo_default_admin_policy'
ASTERISK_AUTOPROV_CONFIG_FILENAME = '/etc/asterisk/pjsip.d/05-autoprov-wizard.conf'
ASTERISK_AUTOPROV_CONFIG_TPL = '''\
[global](+)
default_outbound_endpoint = {username}

[{username}](autoprov-endpoint)
aors = {username}
auth = {username}-auth

[{username}](autoprov-aor)

[{username}-auth]
type = auth
username = {username}
password = {password}
'''

logger = logging.getLogger(__name__)


class WizardService(object):

    def __init__(self, validator, notifier, infos_dao, provd_client, auth_client, sysconfd):
        self.validator = validator
        self.notifier = notifier
        self.infos_dao = infos_dao
        self.provd_client = provd_client
        self.sysconfd = sysconfd
        self._auth_client = auth_client

    def get(self):
        return wizard_db.get_xivo_configured()

    def create(self, wizard):
        self.validator.validate_create(wizard)

        if wizard['steps']['database']:
            with session_scope():
                wizard_db.create(wizard)

        self._send_sysconfd_cmd(
            wizard['network']['hostname'],
            wizard['network']['domain'],
            wizard['network']['nameservers'],
            wizard['steps'],
        )

        if wizard['steps']['provisioning']:
            autoprov_username = self._generate_autoprov_username()
            autoprov_password = self._generate_phone_password(length=8)

            self._initialize_provd(
                wizard['network']['ip_address'],
                autoprov_username,
                autoprov_password,
            )
            self._add_asterisk_autoprov_config(autoprov_username, autoprov_password)
            self.sysconfd.exec_request_handlers({'chown_autoprov_config': []})
            self.sysconfd.flush()
            self.sysconfd.exec_request_handlers({'ipbx': ['module reload res_pjsip.so']})
            self.sysconfd.restart_provd()
            self.sysconfd.dhcpd_update()
            self.sysconfd.flush()

        if wizard['steps']['admin']:
            self._initialize_admin('root', wizard['admin_password'])

        wizard_db.set_xivo_configured()
        self.notifier.created()
        wizard['xivo_uuid'] = self.infos_dao.get().uuid
        return wizard

    def _add_asterisk_autoprov_config(self, autoprov_username, autoprov_password):
        content = ASTERISK_AUTOPROV_CONFIG_TPL.format(
            username=autoprov_username,
            password=autoprov_password,
        )

        try:
            with open(ASTERISK_AUTOPROV_CONFIG_FILENAME, 'w') as fobj:
                fobj.write(content)
        except IOError as e:
            logger.info('%s', e)
            logger.warning('failed to create the Asterisk autoprov configuration file')

    def _send_sysconfd_cmd(self, hostname, domain, nameserver, steps):
        if steps['manage_services']:
            self.sysconfd.xivo_service_enable()
            self.sysconfd.flush()
            self.sysconfd.xivo_service_start()
            self.sysconfd.flush()
        if steps['manage_hosts_file']:
            self.sysconfd.set_hosts(hostname, domain)
        if steps['manage_resolv_file']:
            self.sysconfd.set_resolvconf(nameserver, domain)
        if steps['commonconf']:
            self.sysconfd.commonconf_generate()
            self.sysconfd.flush()
            self.sysconfd.commonconf_apply()
            self.sysconfd.flush()

    def _initialize_admin(self, username, password):
        token = self._auth_client.token.new(expiration=60)['token']
        self._auth_client.set_token(token)
        # user will be in the same tenant as wazo-auth-cli
        user = self._auth_client.users.new(firstname=username, username=username, password=password)
        policy = self._get_policy(DEFAULT_ADMIN_POLICY)
        self._auth_client.users.add_policy(user['uuid'], policy['uuid'])

    def _get_policy(self, policy_name):
        policies = self._auth_client.policies.list(name=policy_name)['items']
        for policy in policies:
            return policy

    def _initialize_provd(self, address, autoprov_username, autoprov_password):
        token = self._auth_client.token.new(expiration=60)['token']
        self.provd_client.set_token(token)
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
        device_config = {'X_type': 'device',
                         'deletable': False,
                         'id': 'defaultconfigdevice',
                         'label': 'Default config device',
                         'parent_ids': [],
                         'raw_config': {'ntp_enabled': True,
                                         'ntp_ip': address,
                                         'sip_dtmf_mode': 'RTP-out-of-band',
                                         'admin_username': 'admin',
                                         'admin_password': self._generate_phone_password(length=16),
                                         'user_username': 'user',
                                         'user_password': self._generate_phone_password(length=16)}}
        autoprov_config = {'X_type': 'internal',
                           'deletable': False,
                           'id': 'autoprov',
                           'parent_ids': ['base', 'defaultconfigdevice'],
                           'raw_config': {'sccp_call_managers': {'1': {'ip': address}},
                                           'sip_lines': {'1': {'display_name': 'Autoprov',
                                                                 'number': 'autoprov',
                                                                 'password': autoprov_password,
                                                                 'proxy_ip': address,
                                                                 'registrar_ip': address,
                                                                 'username': autoprov_username}}},
                           'role': 'autocreate'}

        self.provd_client.configs.create(base_config)
        self.provd_client.configs.create(default_config)
        self.provd_client.configs.create(device_config)
        self.provd_client.configs.create(autoprov_config)

    def _generate_autoprov_username(self):
        suffix = ''.join(random.choice(USERNAME_VALUES) for _ in range(8))
        return 'ap{}'.format(suffix)

    def _generate_phone_password(self, length):
        chars = string.ascii_letters + string.digits
        return "".join(chars[c % len(chars)] for c in urandom(length))

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
        default_gateway = {'gateway': '0.0.0.0', 'interface': None}
        gateways = []
        for gateway in netifaces.gateways().get(netifaces.AF_INET, []):
            gateways.append({'gateway': gateway[0],
                             'interface': gateway[1]})
        gateways.append(default_gateway)
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


def build_service(provd_client, auth_client, infos_dao):
    return WizardService(
        build_validator(),
        build_notifier(),
        infos_dao,
        provd_client,
        auth_client,
        sysconfd,
    )
