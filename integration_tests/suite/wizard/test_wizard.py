# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

import copy
import json
import re

from hamcrest import (assert_that,
                      equal_to,
                      has_entry,
                      has_entries,
                      has_item,
                      has_length,
                      is_not,
                      starts_with)

from xivo_test_helpers import until
from xivo_test_helpers.confd.bus import BusClient
from xivo_test_helpers.confd.wrappers import IsolatedAction

from ..test_api.base import IntegrationTest as BaseIntegrationTest


RESOLVCONF_NAMESERVERS = ['8.8.8.8', '8.8.8.4']
TIMEZONE = 'America/Montreal'
DOMAIN = 'example.com'

COMPLETE_POST_BODY = {'admin_password': 'password',
                      'license': True,
                      'language': 'en_US',
                      'entity_name': 'Test_Entity',
                      'timezone': 'America/Montreal',
                      'network': {'hostname': 'Tutu',
                                  'domain': 'domain.example.com',
                                  'interface': 'eth0',
                                  'ip_address': '127.0.0.1',
                                  'netmask': '255.255.0.0',
                                  'gateway': '127.2.5.1',
                                  'nameservers': ['8.8.8.8', '1.2.3.4']},
                      'context_internal': {'display_name': 'Default',
                                           'number_start': '1000',
                                           'number_end': '1999'},
                      'context_incall': {'display_name': 'Incalls',
                                         'number_start': '2000',
                                         'number_end': '2999',
                                         'did_length': 4},
                      'context_outcall': {'display_name': 'Outcalls'}}

MINIMAL_POST_BODY = {'admin_password': 'password',
                     'license': True,
                     'timezone': 'America/Montreal',
                     'entity_name': 'xivo',
                     'network': {'hostname': 'Tutu',
                                 'domain': 'domain.example.com',
                                 'interface': 'eth0',
                                 'ip_address': '127.0.0.1',
                                 'netmask': '255.255.0.0',
                                 'gateway': '127.2.5.1',
                                 'nameservers': ['8.8.8.8']},
                     'context_internal': {'number_start': '1000',
                                          'number_end': '1999'}}


def build_string(length):
    return ''.join('a' for _ in range(length))


class IntegrationTest(BaseIntegrationTest):
    asset = 'wizard'

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_helpers()
        cls.confd = cls.create_confd()
        cls.provd = cls.create_provd()
        cls.db = cls.create_database()


class mocks(object):
    @classmethod
    class sysconfd(IsolatedAction):

        actions = {'generate': IntegrationTest.setup_sysconfd}


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
        self.check_bogus_field_returns_error('entity_name', ' __  ')
        self.check_bogus_field_returns_error('entity_name', build_string(65))
        self.check_bogus_field_returns_error('entity_name', build_string(2))

    def test_error_timezone(self):
        self.check_bogus_field_returns_error('timezone', 1234)
        self.check_bogus_field_returns_error('timezone', None)
        self.check_bogus_field_returns_error('timezone', True)
        self.check_bogus_field_returns_error('timezone', build_string(129))

    def test_error_hostname(self):
        self.check_network_bogus_field_returns_error('hostname', 1234)
        self.check_network_bogus_field_returns_error('hostname', None)
        self.check_network_bogus_field_returns_error('hostname', True)
        self.check_network_bogus_field_returns_error('hostname', '-bad-regex')
        self.check_network_bogus_field_returns_error('hostname', build_string(64))

    def test_error_domain(self):
        self.check_network_bogus_field_returns_error('domain', 1234)
        self.check_network_bogus_field_returns_error('domain', None)
        self.check_network_bogus_field_returns_error('domain', True)
        self.check_network_bogus_field_returns_error('domain', '-bad-regex')
        self.check_network_bogus_field_returns_error('domain', build_string(256))

    def test_error_interface(self):
        self.check_network_bogus_field_returns_error('interface', 1234)
        self.check_network_bogus_field_returns_error('interface', None)
        self.check_network_bogus_field_returns_error('interface', True)
        self.check_network_bogus_field_returns_error('interface', 'not;valid;interface')
        self.check_network_bogus_field_returns_error('interface', build_string(65))

    def test_error_ip_address(self):
        self.check_network_bogus_field_returns_error('ip_address', 1234)
        self.check_network_bogus_field_returns_error('ip_address', None)
        self.check_network_bogus_field_returns_error('ip_address', True)
        self.check_network_bogus_field_returns_error('ip_address', '1922.162.23.2')

    def test_error_netmask(self):
        self.check_network_bogus_field_returns_error('netmask', 1234)
        self.check_network_bogus_field_returns_error('netmask', None)
        self.check_network_bogus_field_returns_error('netmask', True)
        self.check_network_bogus_field_returns_error('netmask', '1234.192.192.0')

    def test_error_nameservers(self):
        self.check_network_bogus_field_returns_error('nameservers', 1234)
        self.check_network_bogus_field_returns_error('nameservers', None)
        self.check_network_bogus_field_returns_error('nameservers', True)
        self.check_network_bogus_field_returns_error('nameservers', 'string')
        self.check_network_bogus_field_returns_error('nameservers', ['1234.168.0.1'])
        self.check_network_bogus_field_returns_error('nameservers', ['192.168.0.1',
                                                                     '192.168.0.2',
                                                                     '192.168.0.3',
                                                                     '192.168.0.4'])

    def test_error_gateway(self):
        self.check_network_bogus_field_returns_error('gateway', 1234)
        self.check_network_bogus_field_returns_error('gateway', None)
        self.check_network_bogus_field_returns_error('gateway', True)
        self.check_network_bogus_field_returns_error('gateway', '1234.192.192.0')

    def test_error_context_internal_display_name(self):
        self.check_context_internal_bogus_field_returns_error('display_name', 1234)
        self.check_context_internal_bogus_field_returns_error('display_name', None)
        self.check_context_internal_bogus_field_returns_error('display_name', True)
        self.check_context_internal_bogus_field_returns_error('display_name', build_string(2))
        self.check_context_internal_bogus_field_returns_error('display_name', build_string(129))

    def test_error_context_internal_number_start(self):
        self.check_context_internal_bogus_field_returns_error('number_start', 1234)
        self.check_context_internal_bogus_field_returns_error('number_start', None)
        self.check_context_internal_bogus_field_returns_error('number_start', True)
        self.check_context_internal_bogus_field_returns_error('number_start', 'a1234')
        self.check_context_internal_bogus_field_returns_error('number_start', build_string(17))

    def test_error_context_internal_number_end(self):
        self.check_context_internal_bogus_field_returns_error('number_end', 1234)
        self.check_context_internal_bogus_field_returns_error('number_end', None)
        self.check_context_internal_bogus_field_returns_error('number_end', True)
        self.check_context_internal_bogus_field_returns_error('number_end', 'a1234')
        self.check_context_internal_bogus_field_returns_error('number_end', build_string(17))

    def test_error_context_incall_display_name(self):
        self.check_context_incall_bogus_field_returns_error('display_name', 1234)
        self.check_context_incall_bogus_field_returns_error('display_name', None)
        self.check_context_incall_bogus_field_returns_error('display_name', True)
        self.check_context_incall_bogus_field_returns_error('display_name', build_string(2))
        self.check_context_incall_bogus_field_returns_error('display_name', build_string(129))

    def test_error_context_incall_number_start(self):
        self.check_context_incall_bogus_field_returns_error('number_start', 1234)
        self.check_context_incall_bogus_field_returns_error('number_start', None)
        self.check_context_incall_bogus_field_returns_error('number_start', True)
        self.check_context_incall_bogus_field_returns_error('number_start', 'a1234')
        self.check_context_incall_bogus_field_returns_error('number_start', build_string(17))

    def test_error_context_incall_number_end(self):
        self.check_context_incall_bogus_field_returns_error('number_end', 1234)
        self.check_context_incall_bogus_field_returns_error('number_end', None)
        self.check_context_incall_bogus_field_returns_error('number_end', True)
        self.check_context_incall_bogus_field_returns_error('number_end', 'a1234')
        self.check_context_incall_bogus_field_returns_error('number_end', build_string(17))

    def test_error_context_incall_did_length(self):
        self.check_context_incall_bogus_field_returns_error('did_length', None)
        # True is interpreted as 1 = valid
        self.check_context_incall_bogus_field_returns_error('did_length', 'abcd')
        self.check_context_incall_bogus_field_returns_error('did_length', -1)
        self.check_context_incall_bogus_field_returns_error('did_length', 21)

    def test_error_context_outcall_display_name(self):
        self.check_context_outcall_bogus_field_returns_error('display_name', 1234)
        self.check_context_outcall_bogus_field_returns_error('display_name', None)
        self.check_context_outcall_bogus_field_returns_error('display_name', True)
        self.check_context_outcall_bogus_field_returns_error('display_name', build_string(2))
        self.check_context_outcall_bogus_field_returns_error('display_name', build_string(129))

    def check_bogus_field_returns_error(self, field, bogus, sub_field=None):
        body = copy.deepcopy(COMPLETE_POST_BODY)
        if sub_field is None:
            body[field] = bogus
        else:
            body[sub_field][field] = bogus

        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape(field)))

    def check_network_bogus_field_returns_error(self, field, bogus):
        self.check_bogus_field_returns_error(field, bogus, 'network')

    def check_context_internal_bogus_field_returns_error(self, field, bogus):
        self.check_bogus_field_returns_error(field, bogus, 'context_internal')

    def check_context_incall_bogus_field_returns_error(self, field, bogus):
        self.check_bogus_field_returns_error(field, bogus, 'context_incall')

    def check_context_outcall_bogus_field_returns_error(self, field, bogus):
        self.check_bogus_field_returns_error(field, bogus, 'context_outcall')

    def test_context_internal_bad_range(self):
        body = {'context_internal': {'number_start': '3000',
                                     'number_end': '2000'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('context_internal')))

    def test_context_internal_bad_length(self):
        body = {'context_internal': {'number_start': '100',
                                     'number_end': '0199'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('context_internal')))

    def test_context_incall_bad_range(self):
        body = {'context_incall': {'number_start': '3000',
                                   'number_end': '2000'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('context_incall')))

    def test_context_incall_bad_length(self):
        body = {'context_incall': {'number_start': '100',
                                   'number_end': '0199'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('context_incall')))

    def test_context_incall_missing_number(self):
        body = {'context_incall': {'number_start': '2000'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('context_incall')))

    def test_context_incall_missing_did_length(self):
        body = {'context_incall': {'number_start': '2000',
                                   'number_end': '3000'}}
        result = self.confd.wizard.post(body)
        result.assert_match(400, re.compile(re.escape('did_length')))


class TestWizardDiscover(IntegrationTest):

    def test_get_wizard_discover(self):
        docker_status = self.service_status()
        hostname = docker_status['Config']['Hostname']

        network_settings = docker_status['NetworkSettings']
        ip_address = network_settings['IPAddress']
        gateway = network_settings['Gateway']

        expected_response = {
            'domain': DOMAIN,
            'nameservers': RESOLVCONF_NAMESERVERS,
            'hostname': hostname,
            'gateways':  has_item(has_entry('gateway', gateway)),
            'timezone': TIMEZONE,
            'interfaces': has_item(has_entry('ip_address', ip_address))
        }

        response = self.confd.wizard.discover.get()
        assert_that(response.item, has_entries(expected_response))

    def test_wizard_discover_ignores_interface_lo(self):
        expected_response = {
            'interfaces': is_not(has_item(has_entry('interface', 'lo')))
        }

        response = self.confd.wizard.discover.get()
        assert_that(response.item, has_entries(expected_response))


class TestWizardErrorConfigured(IntegrationTest):

    def test_error_configured(self):
        body = copy.deepcopy(MINIMAL_POST_BODY)
        response = self.confd.wizard.post(body)
        response.assert_ok()

        response = self.confd.wizard.post(body)
        response.assert_match(403, re.compile(re.escape('configured')))

        response = self.confd.wizard.discover.get()
        response.assert_match(403, re.compile(re.escape('configured')))


class TestWizardDefaultValue(IntegrationTest):

    def test_default_configuration(self):
        body = copy.deepcopy(MINIMAL_POST_BODY)
        response = self.confd.wizard.post(body)
        response.assert_ok()

        with self.db.queries() as queries:
            assert_that(queries.sip_has_language('en_US'))
            assert_that(queries.iax_has_language('en_US'))
            assert_that(queries.sccp_has_language('en_US'))
            assert_that(queries.context_has_internal('Default',
                                                     body['context_internal']['number_start'],
                                                     body['context_internal']['number_end']))
            assert_that(queries.context_has_incall('Incalls'))
            assert_that(queries.context_has_outcall('Outcalls'))


class TestWizard(IntegrationTest):

    @mocks.sysconfd()
    def test_post(self, sysconfd):
        data = copy.deepcopy(COMPLETE_POST_BODY)
        BusClient.listen_events('config.wizard.created')

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': False}))

        response = self.confd.wizard.post(data)
        response.assert_ok()

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': True}))

        self.validate_db(data)
        self.validate_sysconfd(sysconfd, data)
        self.validate_provd(data['network']['ip_address'])
        self.validate_bus_event()

    def validate_bus_event(self):
        def assert_function():
            assert_that(BusClient.events(), has_length(1))

        until.assert_(assert_function, tries=5)

    def validate_db(self, data):
        with self.db.queries() as queries:
            assert_that(queries.admin_has_password(data['admin_password']))
            assert_that(queries.autoprov_is_configured())
            assert_that(queries.entity_has_name_displayname('testentity', data['entity_name']))
            assert_that(queries.sip_has_language(data['language']))
            assert_that(queries.iax_has_language(data['language']))
            assert_that(queries.sccp_has_language(data['language']))
            assert_that(queries.general_has_timezone(data['timezone']))
            assert_that(queries.resolvconf_is_configured(data['network']['hostname'],
                                                         data['network']['domain'],
                                                         data['network']['nameservers']))
            assert_that(queries.netiface_is_configured(data['network']['ip_address'],
                                                       data['network']['gateway']))
            assert_that(queries.context_has_internal(data['context_internal']['display_name'],
                                                     data['context_internal']['number_start'],
                                                     data['context_internal']['number_end']))
            assert_that(queries.context_has_incall(data['context_incall']['display_name'],
                                                   data['context_incall']['number_start'],
                                                   data['context_incall']['number_end'],
                                                   data['context_incall']['did_length']))
            assert_that(queries.context_has_outcall(data['context_outcall']['display_name']))
            assert_that(queries.context_has_switchboard())
            assert_that(queries.internal_context_include_outcall_context())
            assert_that(queries.profile_as_phonebook_for_lookup())
            assert_that(queries.profile_as_phonebook_for_reverse_lookup())
            assert_that(queries.phonebook_source_is_configured())

    def validate_sysconfd(self, sysconfd, data):
        sysconfd.assert_request('/xivoctl',
                                method='POST',
                                body=json.dumps({'wazo-service': 'enable'}))
        sysconfd.assert_request('/xivoctl',
                                method='POST',
                                body=json.dumps({'wazo-service': 'start'}))
        sysconfd.assert_request('/hosts',
                                method='POST',
                                body=json.dumps({'hostname': data['network']['hostname'],
                                                 'domain': data['network']['domain']}))
        sysconfd.assert_request('/resolv_conf',
                                method='POST',
                                body=json.dumps({'nameservers': data['network']['nameservers'],
                                                 'search': [data['network']['domain']]}))
        sysconfd.assert_request('/commonconf_generate',
                                method='POST',
                                body=json.dumps({}))
        sysconfd.assert_request('/commonconf_apply',
                                method='GET')

    def validate_provd(self, ip_address):
        configs = self.provd.configs.find()

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
                             u'sip_dtmf_mode': u'RTP-out-of-band'}}
        ]

        assert_that(configs, equal_to(expected_config))
