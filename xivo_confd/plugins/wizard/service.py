# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
PHONEBOOK_BODY = {'name': 'wazo'}


class WizardService(object):

    def __init__(self, validator, notifier, tenant_dao, infos_dao, provd_client, auth_client, dird_client, sysconfd):
        self.validator = validator
        self.notifier = notifier
        self.tenant_dao = tenant_dao
        self.infos_dao = infos_dao
        self.provd_client = provd_client
        self.sysconfd = sysconfd
        self._auth_client = auth_client
        self._dird_client = dird_client

    def get(self):
        return wizard_db.get_xivo_configured()

    def create(self, wizard):
        self.validator.validate_create(wizard)
        autoprov_username = self._generate_autoprov_username()
        tenant_uuid = self.tenant_dao.find().uuid

        if wizard['steps']['database']:
            with session_scope():
                wizard_db.create(wizard, autoprov_username, tenant_uuid)

        self._send_sysconfd_cmd(wizard['network']['hostname'],
                                wizard['network']['domain'],
                                wizard['network']['nameservers'],
                                wizard['steps'])
        if wizard['steps']['provisioning']:
            self._initialize_provd(wizard['network']['ip_address'], autoprov_username)
        entity_display_name = wizard['entity_name']
        entity_unique_name = wizard_db.entity_unique_name(entity_display_name)
        if wizard['steps']['phonebook']:
            self._initialize_phonebook(entity_unique_name)
        if wizard['steps']['tenant']:
            self._initialize_tenant(tenant_uuid, entity_unique_name)

        wizard_db.set_xivo_configured()
        self.notifier.created()
        wizard['xivo_uuid'] = self.infos_dao.get().uuid
        return wizard

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

    def _initialize_phonebook(self, entity):
        token = self._auth_client.token.new('xivo_service', expiration=60)['token']
        phonebook = self._dird_client.phonebook.create(tenant=entity, phonebook_body=PHONEBOOK_BODY, token=token)
        wizard_db.set_phonebook(entity, phonebook)

    def _initialize_tenant(self, tenant_uuid, tenant_name):
        token = self._auth_client.token.new('xivo_service', expiration=60)['token']
        self._auth_client.set_token(token)
        self._auth_client.tenants.new(uuid=str(tenant_uuid), name=tenant_name)

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
                                         u'sip_dtmf_mode': u'RTP-out-of-band',
                                         u'admin_username': 'admin',
                                         u'admin_password': self._generate_phone_password(length=16),
                                         u'user_username': 'user',
                                         u'user_password': self._generate_phone_password(length=16)}}
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

    def _generate_phone_password(self, length):
        chars = string.ascii_letters + string.digits
        return "".join(chars[ord(c) % len(chars)] for c in urandom(length))

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


def build_service(provd_client, auth_client, dird_client, tenant_dao, infos_dao):
    return WizardService(
        build_validator(),
        build_notifier(),
        tenant_dao,
        infos_dao,
        provd_client,
        auth_client,
        dird_client,
        sysconfd,
    )
