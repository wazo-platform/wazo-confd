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
from hamcrest import (assert_that,
                      equal_to,
                      has_item,
                      contains_string,
                      starts_with)

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from test_api import confd, provd, db, mocks

RESOLVCONF_NAMESERVERS = ['8.8.8.8', '8.8.8.4']
TIMEZONE = 'America/Montreal'


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

    def setUp(self):
        super(TestWizardErrors, self).setUp()
        self.default_body = {'admin_password': 'password',
                             'license': True,
                             'language': 'en_US',
                             'entity_name': 'Test_Entity',
                             'network': {'hostname': 'Tutu',
                                         'domain': 'domain.test.com',
                                         'ip_address': self.ip_address}}

    def test_do_not_accept_license(self):
        body = self.default_body
        body['license'] = False
        result = confd.wizard.post(body)
        assert_that(result.status, equal_to(400))
        assert_that(result.json, has_item(contains_string('license')))

    def test_not_boolean_lincense(self):
        body = self.default_body
        body['license'] = 'asdf'
        result = confd.wizard.post(body)
        assert_that(result.status, equal_to(400))
        assert_that(result.json, has_item(contains_string('license')))


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
