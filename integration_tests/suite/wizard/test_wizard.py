# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import json
import re

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    empty,
    has_entry,
    has_entries,
    has_item,
    has_length,
    is_not,
    starts_with,
)

from xivo_test_helpers import until

from ..helpers.wrappers import IsolatedAction
from ..helpers.base import IntegrationTest as BaseIntegrationTest


RESOLVCONF_NAMESERVERS = ['127.0.0.11']
TIMEZONE = 'America/Montreal'
DOMAIN = 'example.com'

COMPLETE_POST_BODY = {
    'admin_password': 'password',
    'license': True,
    'language': 'en_US',
    'timezone': 'America/Montreal',
    'network': {
        'hostname': 'Tutu',
        'domain': 'domain.example.com',
        'interface': 'eth0',
        'ip_address': '127.0.0.1',
        'netmask': '255.255.0.0',
        'gateway': '127.2.5.1',
        'nameservers': ['8.8.8.8', '1.2.3.4']
    },
    'steps': {
        'database': True,
        'manage_services': True,
        'manage_hosts_file': True,
        'manage_resolv_file': True,
        'commonconf': True,
        'provisioning': True,
        'admin': True,
    }
}

MINIMAL_POST_BODY = {
    'admin_password': 'password',
    'license': True,
    'timezone': 'America/Montreal',
    'network': {
        'hostname': 'Tutu',
        'domain': 'domain.example.com',
        'interface': 'eth0',
        'ip_address': '127.0.0.1',
        'netmask': '255.255.0.0',
        'gateway': '127.2.5.1',
        'nameservers': ['8.8.8.8']
    },
}

DISABLED_STEPS_POST_BODY = {
    'admin_password': 'password',
    'license': True,
    'timezone': 'America/Montreal',
    'network': {
        'hostname': 'Tutu',
        'domain': 'domain.example.com',
        'interface': 'eth0',
        'ip_address': '127.0.0.1',
        'netmask': '255.255.0.0',
        'gateway': '127.2.5.1',
        'nameservers': ['8.8.8.8']},
    'steps': {
        'database': False,
        'manage_services': False,
        'manage_hosts_file': False,
        'manage_resolv_file': False,
        'commonconf': False,
        'provisioning': False,
        'admin': False,
    }
}


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
        cls.bus = cls.create_bus()


class mocks:
    @classmethod
    class sysconfd(IsolatedAction):

        actions = {'generate': IntegrationTest.setup_sysconfd}

    @classmethod
    class auth(IsolatedAction):

        actions = {'generate': IntegrationTest.setup_auth}


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
        self.check_network_bogus_field_returns_error(
            'nameservers', ['192.168.0.1', '192.168.0.2', '192.168.0.3', '192.168.0.4']
        )

    def test_error_gateway(self):
        self.check_network_bogus_field_returns_error('gateway', 1234)
        self.check_network_bogus_field_returns_error('gateway', None)
        self.check_network_bogus_field_returns_error('gateway', True)
        self.check_network_bogus_field_returns_error('gateway', '1234.192.192.0')

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


class TestWizardDiscover(IntegrationTest):

    def test_get_wizard_discover(self):
        docker_status = self.service_status()
        hostname = docker_status['Config']['Hostname']

        network_settings = docker_status['NetworkSettings']['Networks']['confd_default']
        ip_address = network_settings['IPAddress']
        gateway = network_settings['Gateway']

        response = self.confd.wizard.discover.get()
        assert_that(
            response.item,
            has_entries(
                domain=DOMAIN,
                nameservers=RESOLVCONF_NAMESERVERS,
                hostname=hostname,
                gateways=has_item(has_entry('gateway', gateway)),
                timezone=TIMEZONE,
                interfaces=has_item(has_entry('ip_address', ip_address)),
            )
        )

    def test_wizard_discover_ignores_interface_lo(self):
        response = self.confd.wizard.discover.get()
        assert_that(
            response.item,
            has_entries(interfaces=is_not(has_item(has_entry('interface', 'lo'))))
        )


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


class TestWizard(IntegrationTest):

    @mocks.sysconfd()
    @mocks.auth()
    def test_post(self, sysconfd, auth):
        data = copy.deepcopy(COMPLETE_POST_BODY)
        bus_events = self.bus.accumulator('config.wizard.created')

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': False}))

        response = self.confd.wizard.post(data)
        response.assert_ok()

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': True}))

        self.validate_db(data)
        self.validate_auth(auth, data)
        self.validate_sysconfd(sysconfd, data)
        self.validate_provd(data['network']['ip_address'])

        def assert_bus_event_received():
            assert_that(bus_events.accumulate(), has_length(1))

        until.assert_(assert_bus_event_received, tries=5)

    def validate_db(self, data):
        with self.db.queries() as queries:
            assert_that(queries.sip_has_language(data['language']))
            assert_that(queries.iax_has_language(data['language']))
            assert_that(queries.sccp_has_language(data['language']))
            assert_that(queries.general_has_timezone(data['timezone']))
            assert_that(queries.resolvconf_is_configured(
                data['network']['hostname'],
                data['network']['domain'],
                data['network']['nameservers']
            ))
            assert_that(queries.netiface_is_configured(
                data['network']['ip_address'],
                data['network']['gateway']
            ))

    def validate_auth(self, auth, data):
        auth.assert_request(
            '/0.1/users',
            method='POST',
            json={
                'username': 'root',
                'password': data['admin_password'],
                'firstname': 'root'
            }
        )
        auth.assert_request(
            r'^/0.1/users/.{36}/policies/.{36}$',
            method='PUT',
        )

    def validate_sysconfd(self, sysconfd, data):
        sysconfd.assert_request(
            '/xivoctl',
            method='POST',
            json={'wazo-service': 'enable'},
        )
        sysconfd.assert_request(
            '/xivoctl',
            method='POST',
            json={'wazo-service': 'start'},
        )
        sysconfd.assert_request(
            '/hosts',
            method='POST',
            json={
                'hostname': data['network']['hostname'],
                'domain': data['network']['domain']
            },
        )
        sysconfd.assert_request(
            '/resolv_conf',
            method='POST',
            json={
                'nameservers': data['network']['nameservers'],
                'search': [data['network']['domain']]
            },
        )
        sysconfd.assert_request(
            '/commonconf_generate',
            method='POST',
            json={},
        )
        sysconfd.assert_request(
            '/commonconf_apply',
            method='GET'
        )
        sysconfd.assert_request(
            '/exec_request_handlers',
            method='POST',
            json={'chown_autoprov_config': []},
        )
        sysconfd.assert_request(
            '/exec_request_handlers',
            method='POST',
            json={'ipbx': ['module reload res_pjsip.so']},
        )

    def validate_provd(self, ip_address):
        configs = self.provd.configs.list()['configs']

        assert_that(
            configs,
            contains_inanyorder(
                has_entries(
                    X_type='registrar',
                    deletable=False,
                    displayname='local',
                    id='default',
                    parent_ids=[],
                    proxy_main=ip_address,
                    raw_config={'X_key': 'xivo'},
                    registrar_main=ip_address,
                ),
                has_entries(
                    X_type='internal',
                    deletable=False,
                    id='autoprov',
                    parent_ids=['base', 'defaultconfigdevice'],
                    raw_config=has_entries(
                        sccp_call_managers={'1': {'ip': ip_address}},
                        sip_lines=has_entries(
                            '1', has_entries(
                                display_name='Autoprov',
                                number='autoprov',
                                password=has_length(8),
                                proxy_ip=ip_address,
                                registrar_ip=ip_address,
                                username=starts_with('ap')
                            )
                        )
                    ),
                    role='autocreate',
                ),
                has_entries(
                    X_type='internal',
                    deletable=False,
                    id='base',
                    parent_ids=[],
                    raw_config={
                        'X_xivo_phonebook_ip': ip_address,
                        'ntp_enabled': True,
                        'ntp_ip': ip_address,
                    },
                ),
                has_entries(
                    X_type='device',
                    deletable=False,
                    id='defaultconfigdevice',
                    label='Default config device',
                    parent_ids=[],
                    raw_config=has_entries(
                        ntp_enabled=True,
                        ntp_ip=ip_address,
                        X_xivo_phonebook_ip=ip_address,
                        sip_dtmf_mode='RTP-out-of-band',
                        admin_username='admin',
                        admin_password=has_length(16),
                        user_username='user',
                        user_password=has_length(16)
                    )
                )
            )
        )


class TestWizardSteps(IntegrationTest):

    @mocks.sysconfd()
    @mocks.auth()
    def test_post(self, sysconfd, auth):
        data = copy.deepcopy(DISABLED_STEPS_POST_BODY)
        bus_events = self.bus.accumulator('config.wizard.created')

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': False}))

        response = self.confd.wizard.post(data)
        response.assert_ok()

        response = self.confd.wizard.get()
        assert_that(response.item, equal_to({'configured': True}))

        self.validate_auth(auth, data)
        self.validate_sysconfd(sysconfd, data)
        self.validate_provd()

        def assert_bus_event_received():
            assert_that(bus_events.accumulate(), has_length(1))

        until.assert_(assert_bus_event_received, tries=5)

    def validate_auth(self, auth, data):
        auth.assert_no_request(
            '/0.1/users',
            method='POST',
        )
        auth.assert_no_request(
            r'^/0.1/users/.{36}/policies/.{36}$',
            method='PUT',
        )

    def validate_sysconfd(self, sysconfd, data):
        sysconfd.assert_no_request(
            '/xivoctl',
            method='POST',
            body=json.dumps({'wazo-service': 'enable'})
        )
        sysconfd.assert_no_request(
            '/hosts',
            method='POST',
            body=json.dumps({
                'hostname': data['network']['hostname'],
                'domain': data['network']['domain']
            })
        )
        sysconfd.assert_no_request(
            '/resolv_conf',
            method='POST',
            body=json.dumps({
                'nameservers': data['network']['nameservers'],
                'search': [data['network']['domain']]
            })
        )
        sysconfd.assert_no_request(
            '/commonconf_generate',
            method='POST',
            body=json.dumps({})
        )

    def validate_provd(self):
        configs = self.provd.configs.list()['configs']

        assert_that(configs, empty())
