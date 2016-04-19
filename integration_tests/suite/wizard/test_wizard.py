# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import json
import re

from hamcrest import (assert_that,
                      equal_to,
                      starts_with)

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from test_api import confd, provd, db, mocks

RESOLVCONF_NAMESERVERS = ['8.8.8.8', '8.8.8.4']
TIMEZONE = 'America/Montreal'


def build_string(length):
    return ''.join('a' for _ in range(length))


class IntegrationTest(AssetLaunchingTestCase):

    assets_root = 'assets'
    service = 'confd'
    asset = 'wizard'

    def setUp(self):
        super(IntegrationTest, self).setUp()
        network_settings = self.service_status()['NetworkSettings']
        self.ip_address = network_settings['IPAddress']
        self.gateway = network_settings['Gateway']


class TestWizardErrors(IntegrationTest):

    def test_error_license(self):
        self.check_bogus_field_returns_error('license', 1234)
        self.check_bogus_field_returns_error('license', 'asdf')
        self.check_bogus_field_returns_error('license', False)

    def test_error_password(self):
        self.check_bogus_field_returns_error('admin_password', 1234)
        self.check_bogus_field_returns_error('admin_password', None)
        self.check_bogus_field_returns_error('admin_password', True)
        self.check_bogus_field_returns_error('admin_password', 'invalidé')
        self.check_bogus_field_returns_error('admin_password', build_string(65))
        self.check_bogus_field_returns_error('admin_password', build_string(3))

    def test_error_language(self):
        self.check_bogus_field_returns_error('language', 1234)
        self.check_bogus_field_returns_error('language', None)
        self.check_bogus_field_returns_error('language', True)
        self.check_bogus_field_returns_error('language', 'fr_US')

    def test_error_entity_name(self):
        self.check_bogus_field_returns_error('entity_name', 1234)
        self.check_bogus_field_returns_error('entity_name', None)
        self.check_bogus_field_returns_error('entity_name', True)
        self.check_bogus_field_returns_error('entity_name', build_string(65))
        self.check_bogus_field_returns_error('entity_name', build_string(2))

    def test_error_hostname(self):
        self.check_bogus_field_returns_error('hostname', 1234)
        self.check_bogus_field_returns_error('hostname', None)
        self.check_bogus_field_returns_error('hostname', True)
        self.check_bogus_field_returns_error('hostname', '-bad-regex')
        self.check_bogus_field_returns_error('hostname', build_string(64))

    def test_error_domain(self):
        self.check_bogus_field_returns_error('domain', 1234)
        self.check_bogus_field_returns_error('domain', None)
        self.check_bogus_field_returns_error('domain', True)
        self.check_bogus_field_returns_error('domain', '-bad-regex')
        self.check_bogus_field_returns_error('domain', build_string(256))

    def test_error_ip_address(self):
        self.check_bogus_field_returns_error('ip_address', 1234)
        self.check_bogus_field_returns_error('ip_address', None)
        self.check_bogus_field_returns_error('ip_address', True)
        self.check_bogus_field_returns_error('ip_address', '1922.162.23.2')

    def check_bogus_field_returns_error(self, field, bogus):
        body = {'admin_password': 'password',
                'license': True,
                'language': 'en_US',
                'entity_name': 'Test_Entity',
                'network': {'hostname': 'Tutu',
                            'domain': 'domain.test.com',
                            'ip_address': self.ip_address}}
        if field in body:
            body[field] = bogus
        else:
            body['network'][field] = bogus

        result = confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape(field)))


class TestWizardErrorConfigured(IntegrationTest):

    def test_error_ip_address(self):
        body = {'admin_password': 'password',
                'license': True,
                'language': 'en_US',
                'entity_name': 'Test_Entity',
                'network': {'hostname': 'Tutu',
                            'domain': 'domain.test.com',
                            'ip_address': self.ip_address}}
        response = confd.wizard.post(body)
        response.assert_ok()

        response = confd.wizard.post(body)
        response.assert_match(400, re.compile(re.escape('configured')))


class TestWizard(IntegrationTest):

    @mocks.sysconfd()
    def test_post(self, sysconfd):
        data = {'admin_password': 'password',
                'license': True,
                'language': 'en_US',
                'entity_name': 'Test_Entity',
                'network': {'hostname': 'Tutu',
                            'domain': 'domain.test.com',
                            'ip_address': self.ip_address}}

        response = confd.wizard.get()
        assert_that(response.item, equal_to({'configured': False}))

        response = confd.wizard.post(data)
        response.assert_ok()

        response = confd.wizard.get()
        assert_that(response.item, equal_to({'configured': True}))

        self.validate_db(data, self.ip_address, self.gateway)
        self.validate_sysconfd(sysconfd, data)
        self.validate_provd(self.ip_address, self.gateway)

    def validate_db(self, data, ip_address, gateway):
        with db.queries() as queries:
            assert_that(queries.admin_has_password(data['admin_password']))
            assert_that(queries.autoprov_is_configured())
            assert_that(queries.entity_has_name_displayname('testentity', data['entity_name']))
            assert_that(queries.sip_has_language(data['language']))
            assert_that(queries.iax_has_language(data['language']))
            assert_that(queries.sccp_has_language(data['language']))
            assert_that(queries.general_has_timezone(TIMEZONE))
            assert_that(queries.resolvconf_is_configured(data['network']['hostname'],
                                                         data['network']['domain'],
                                                         RESOLVCONF_NAMESERVERS))
            assert_that(queries.netiface_is_configured(ip_address, gateway))

    def validate_sysconfd(self, sysconfd, data):
        sysconfd.assert_request('/xivoctl',
                                method='POST',
                                body=json.dumps({'xivo-service': 'enable'}))
        sysconfd.assert_request('/xivoctl',
                                method='POST',
                                body=json.dumps({'xivo-service': 'start'}))
        sysconfd.assert_request('/hosts',
                                method='POST',
                                body=json.dumps({'hostname': data['network']['hostname'],
                                                 'domain': data['network']['domain']}))
        sysconfd.assert_request('/resolv_conf',
                                method='POST',
                                body=json.dumps({'nameservers': RESOLVCONF_NAMESERVERS,
                                                 'search': [data['network']['domain']]}))
        sysconfd.assert_request('/commonconf_generate',
                                method='POST',
                                body=json.dumps({}))
        sysconfd.assert_request('/commonconf_apply',
                                method='GET')

    def validate_provd(self, ip_address, gateway):
        configs = provd.configs.find()

        autoprov_username = configs[1]['raw_config']['sip_lines']['1']['username']
        assert_that(autoprov_username, starts_with('ap'))

        expected_config = [
            {u'X_type': u'registrar',
             u'deletable': False,
             u'displayname': u'local',
             u'id': u'default',
             u'parent_ids': [],
             u'proxy_main': ip_address,
             u'raw_config': {u'X_key': u'xivo'},
             u'registrar_main': ip_address},
            {u'X_type': u'internal',
             u'deletable': False,
             u'id': u'autoprov',
             u'parent_ids': [u'base', u'defaultconfigdevice'],
             u'raw_config': {u'sccp_call_managers': {u'1': {u'ip': ip_address}},
                             u'sip_lines': {u'1': {u'display_name': u'Autoprov',
                                                   u'number': u'autoprov',
                                                   u'password': u'autoprov',
                                                   u'proxy_ip': ip_address,
                                                   u'registrar_ip': ip_address,
                                                   u'username': autoprov_username}}},
             u'role': u'autocreate'},
            {u'X_type': u'internal',
             u'deletable': False,
             u'id': u'base',
             u'parent_ids': [],
             u'raw_config': {u'X_xivo_phonebook_ip': ip_address,
                             u'ntp_enabled': True,
                             u'ntp_ip': ip_address}},
            {u'X_type': u'device',
             u'deletable': False,
             u'id': u'defaultconfigdevice',
             u'label': u'Default config device',
             u'parent_ids': [],
             u'raw_config': {u'ntp_enabled': True,
                             u'ntp_ip': ip_address,
                             u'sip_dtmf_mode': u'SIP-INFO'}}
        ]

        assert_that(configs, equal_to(expected_config))
