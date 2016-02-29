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
from test_api import helpers as h
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
                      has_item,
                      starts_with,
                      contains,
                      empty)


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
    fake_get = confd.devices(999999).get
    yield s.check_resource_not_found, fake_get, 'Device'


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


@fixtures.device(ip="10.20.30.40",
                 mac="aa:bb:aa:cc:01:23",
                 model="SearchModel",
                 plugin='zero',
                 sn="SearchSn",
                 vendor='SearchVendor',
                 version='1.0',
                 description='SearchDesc')
@fixtures.device(ip="11.22.33.44",
                 mac="dd:ee:dd:ff:45:67",
                 model="HiddenModel",
                 plugin='null',
                 sn="HiddenSn",
                 vendor="HiddenVendor",
                 version="2.0",
                 description="HiddenDesc")
def test_search_on_device(device, hidden):
    url = confd.devices
    searches = {'ip': '20.30',
                'mac': 'bb:aa',
                'model': 'chmod',
                'plugin': 'zer',
                'sn': 'chsn',
                'vendor': 'chven',
                'version': '1.0',
                'description': 'rchdes'}

    for field, term in searches.items():
        yield check_search, url, device, hidden, field, term


@fixtures.device(ip="99.20.30.40",
                 mac="aa:bb:aa:cc:01:23",
                 model="SortModel1",
                 sn="SortSn1",
                 vendor='SortVendor1',
                 version='1.0',
                 description='SortDesc1')
@fixtures.device(ip="99.21.30.40",
                 mac="bb:cc:dd:aa:bb:cc",
                 model="SortModel2",
                 sn="SortSn2",
                 vendor="SortVendor2",
                 version="1.1",
                 description="SortDesc2")
def test_device_sorting(device1, device2):
    yield check_device_sorting, device1, device2, 'ip', '99.'
    yield check_device_sorting, device1, device2, 'model', 'SortModel'
    yield check_device_sorting, device1, device2, 'sn', 'SortSn'
    yield check_device_sorting, device1, device2, 'vendor', 'SortVendor'
    yield check_device_sorting, device1, device2, 'version', '1.'
    yield check_device_sorting, device1, device2, 'description', 'SortDesc'


def check_device_sorting(device1, device2, field, search):
    response = confd.devices.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=device1['id']),
                                         has_entries(id=device2['id'])))

    response = confd.devices.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=device2['id']),
                                         has_entries(id=device1['id'])))


def check_search(url, device, hidden, field, term):
    response = url.get(search=term)

    expected_device = has_item(has_entry(field, device[field]))
    hidden_device = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_device)
    assert_that(response.items, hidden_device)


@fixtures.device(template_id="mockdevicetemplate",
                 plugin='zero',
                 vendor='myvendor',
                 version='1.0',
                 description='getdevice',
                 options={'switchboard': True})
def test_get(device):
    response = confd.devices(device['id']).get()
    assert_that(response.item, has_entries(ip=device['ip'],
                                           mac=device['mac'],
                                           template_id="mockdevicetemplate",
                                           plugin='zero',
                                           vendor='myvendor',
                                           version='1.0',
                                           description='getdevice',
                                           options={'switchboard': True}))


def test_create_device_minimal_parameters():
    response = confd.devices.post()
    response.assert_created('devices')

    provd_device = provd.devices.get(response.item['id'])
    assert_that(provd_device['config'], starts_with('autoprov'))


def test_create_device_all_parameters():
    mac, ip = h.device.generate_mac_and_ip()
    template_config = provd.configs.find({'id': 'mockdevicetemplate'})[0]

    parameters = {'ip': ip,
                  'mac': mac,
                  'model': '6731i',
                  'plugin': 'null',
                  'sn': 'sn',
                  'template_id': 'mockdevicetemplate',
                  'vendor': 'Aastra',
                  'version': '1.0',
                  'description': 'mydevice',
                  'options': {'switchboard': True}}

    response = confd.devices.post(**parameters)
    response.assert_created('devices')
    assert_that(response.item, has_entries(parameters))

    provd_device = provd.devices.get(response.item['id'])
    assert_that(provd_device, has_entries({'ip': ip,
                                           'mac': mac,
                                           'model': '6731i',
                                           'plugin': 'null',
                                           'sn': 'sn',
                                           'vendor': 'Aastra',
                                           'version': '1.0',
                                           'description': 'mydevice',
                                           'options': {'switchboard': True}}))

    provd_config = provd.configs.get(provd_device['config'])
    assert_that(provd_config['id'], starts_with('autoprov'))
    assert_that(provd_config['parent_ids'], has_item(template_config['id']))


@fixtures.device()
def test_create_2_devices_with_same_mac(device):
    response = confd.devices.post(mac=device['mac'])
    response.assert_match(400, e.resource_exists('Device'))


@fixtures.device()
def test_create_2_devices_with_same_ip(device):
    response = confd.devices.post(ip=device['ip'])
    response.assert_created('devices')


def test_create_device_with_fake_plugin():
    response = confd.devices.post(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


def test_create_device_with_fake_template():
    response = confd.devices.post(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


@fixtures.device(plugin='zero', template_id='defaultconfigdevice')
def test_edit_device_all_parameters(device):
    mac, ip = h.device.generate_mac_and_ip()
    parameters = {'ip': ip,
                  'mac': mac,
                  'model': '6731i',
                  'plugin': 'null',
                  'sn': 'sn',
                  'template_id': 'mockdevicetemplate',
                  'vendor': 'Aastra',
                  'version': '1.0',
                  'description': 'mydevice',
                  'options': {'switchboard': True}}

    response = confd.devices(device['id']).put(**parameters)
    response.assert_updated()

    response = confd.devices(device['id']).get()
    assert_that(response.item, has_entries(parameters))


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
def test_delete_device(device):
    response = confd.devices(device['id']).delete()
    response.assert_deleted()

    provd_devices = provd.devices.find({'id': device['id']})
    assert_that(provd_devices, empty())


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
