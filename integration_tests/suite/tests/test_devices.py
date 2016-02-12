# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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

import unittest

from datetime import datetime

from test_api import mocks
from test_api import scenarios as s
from test_api import errors as e
from test_api import associations as a
from test_api import fixtures
from test_api import confd
from test_api import provd

from hamcrest import (assert_that,
                      has_entry,
                      has_entries,
                      has_key,
                      none,
                      not_none,
                      is_not,
                      starts_with)


BOGUS = [
    ('ip', 'aelkurxynsle', 'IP address'),
    ('mac', 'o374awic87anwc', 'MAC address'),
    ('sn', 123, 'unicode string'),
    ('vendor', 123, 'unicode string'),
    ('model', 123, 'unicode string'),
    ('version', 123, 'unicode string'),
    ('plugin', 123, 'unicode string'),
    ('description', 123, 'unicode string'),
    ('template_id', 123, 'unicode string'),
    ('options', 123, 'dict-like structure'),
]


class TestDeviceCreateWithTemplate(unittest.TestCase):

    def setUp(self):
        self.provd = provd
        self.provd.reset()
        self.template_id = self.provd.add_device_template()

    def tearDown(self):
        self.provd.reset()

    def test_create_device_with_template(self):
        response = confd.devices.post(template_id=self.template_id)
        response.assert_status(201)

        device_id = response.json[u'id']
        device = self.provd.devices.get(device_id)
        config = self.provd.configs.get(device[u'config'])
        self.provd.assert_device_has_autoprov_config(device)
        self.provd.assert_config_use_device_template(config, self.template_id)
        self.provd.assert_config_does_not_exist(device_id)


def test_get_errors():
    fake_sip_get = confd.endpoints.sip(999999).get
    yield s.check_resource_not_found, fake_sip_get, 'SIPEndpoint'


def test_post_errors():
    url = confd.devices.post
    for check in error_checks(url):
        yield check


@fixtures.device()
def test_put_errors(device):
    url = confd.devices(device['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'ip', 123
    yield s.check_bogus_field_returns_error, url, 'ip', 'abcd1234'
    yield s.check_bogus_field_returns_error, url, 'mac', 123
    yield s.check_bogus_field_returns_error, url, 'mac', 'abcd1234'
    yield s.check_bogus_field_returns_error, url, 'mac', 'abcd1234'
    yield s.check_bogus_field_returns_error, url, 'plugin', 'invalidplugin'
    yield s.check_bogus_field_returns_error, url, 'template_id', 'invalidtemplateid'
    yield s.check_bogus_field_returns_error, url, 'options', 'invalidoption'
    yield s.check_bogus_field_returns_error, url, 'options', {'switchboard': 'yes'}


@fixtures.device()
def test_create_2_devices_with_same_mac(device):
    response = confd.devices.post(mac=device['mac'])
    response.assert_match(400, e.resource_exists('Device'))


def test_create_device_with_fake_plugin():
    response = confd.devices.post(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


def test_create_device_with_fake_template():
    response = confd.devices.post(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


@fixtures.device()
@fixtures.device()
def test_edit_device_with_same_mac(first_device, second_device):
    response = confd.devices(first_device['id']).put(mac=second_device['mac'])
    response.assert_match(400, e.resource_exists('Device'))


@fixtures.device()
def test_edit_device_with_fake_plugin(device):
    response = confd.devices(device['id']).put(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


@fixtures.device()
def test_edit_device_with_fake_template(device):
    response = confd.devices(device['id']).put(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


@fixtures.device()
@fixtures.line()
def test_associate_line_to_a_device(device, line):
    response = confd.devices(device['id']).associate_line(line['id']).get()
    response.assert_status(403)


@fixtures.device()
@fixtures.line()
def test_dissociate_line_to_a_device(device, line):
    response = confd.devices(device['id']).remove_line(line['id']).get()
    response.assert_status(403)


@mocks.provd()
@fixtures.device()
@fixtures.line()
def test_reset_to_autoprov_device_associated_to_line(provd, device, line):
    with a.line_device(line, device, check=False):
        response = confd.devices(device['id']).autoprov.get()
        response.assert_ok()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entry('device_id', none()))

        device_cfg = provd.devices.get(device['id'])
        assert_that(device_cfg, has_entries(config=starts_with('autoprov')))
        assert_that(device_cfg, is_not(has_key('options')))

        config_cfg = provd.configs.get(device_cfg['config'])
        assert_that(config_cfg, not_none())

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries(device_id=none()))


@mocks.provd()
@fixtures.device()
def test_synchronize_device(provd, device):
    timestamp = datetime.utcnow()

    response = confd.devices(device['id']).synchronize.get()
    response.assert_ok()

    synchonized = provd.has_synchronized(device['id'], timestamp)
    assert_that(synchonized, "Device was not synchronized")
