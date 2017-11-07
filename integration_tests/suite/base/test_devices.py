# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import unittest

from datetime import datetime

from ..test_api import helpers as h
from ..test_api import scenarios as s
from ..test_api import errors as e
from ..test_api import associations as a
from ..test_api import fixtures
from . import confd
from . import mocks, provd

from hamcrest import (assert_that,
                      has_entry,
                      has_entries,
                      has_key,
                      none,
                      not_none,
                      is_not,
                      has_item,
                      starts_with,
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


def test_search_errors():
    url = confd.devices.get
    for check in s.search_error_checks(url):
        yield check


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
def test_search(device, hidden):
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


def check_search(url, device, hidden, field, term):
    response = url.get(search=term)

    expected_device = has_item(has_entry(field, device[field]))
    hidden_device = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_device)
    assert_that(response.items, hidden_device)

    response = url.get(**{field: device[field]})

    expected_device = has_item(has_entry('id', device['id']))
    hidden_device = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_device)
    assert_that(response.items, hidden_device)


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
def test_sorting_offset_limit(device1, device2):
    url = confd.devices.get
    yield s.check_sorting, url, device1, device2, 'ip', '99.'
    yield s.check_sorting, url, device1, device2, 'model', 'SortModel'
    yield s.check_sorting, url, device1, device2, 'sn', 'SortSn'
    yield s.check_sorting, url, device1, device2, 'vendor', 'SortVendor'
    yield s.check_sorting, url, device1, device2, 'version', '1.'
    yield s.check_sorting, url, device1, device2, 'description', 'SortDesc'

    yield s.check_offset, url, device1, device2, 'mac', 'aa:bb'
    yield s.check_offset_legacy, url, device1, device2, 'mac', 'aa:bb'

    yield s.check_limit, url, device1, device2, 'mac', 'aa:bb'


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

    assert_that(response.item, has_entries(mac=none(),
                                           template_id=none(),
                                           status='not_configured',
                                           plugin=none(),
                                           vendor=none(),
                                           version=none(),
                                           description=none(),
                                           options=none()))

    provd_device = provd.devices.get(response.item['id'])
    assert_that(provd_device['config'], starts_with('autoprov'))


def test_create_device_null_parameters():
    response = confd.devices.post(mac=None,
                                  template_id=None,
                                  plugin=None,
                                  vendor=None,
                                  version=None,
                                  description=None,
                                  options=None)
    response.assert_created('devices')

    assert_that(response.item, has_entries(mac=none(),
                                           template_id=none(),
                                           status='not_configured',
                                           plugin=none(),
                                           vendor=none(),
                                           version=none(),
                                           description=none(),
                                           options=none()))

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


@fixtures.device(ip="127.8.0.8",
                 mac="a1:b1:c1:d1:e1:f1",
                 model='6731i',
                 plugin='zero',
                 sn='sn',
                 template_id='defaultconfigdevice',
                 vendor='1.0',
                 description='nullparameters',
                 options={'switchboard': True})
def test_edit_device_null_parameters(device):
    url = confd.devices(device['id'])
    response = url.put(mac=None,
                       template_id=None,
                       plugin=None,
                       vendor=None,
                       version=None,
                       description=None,
                       options=None)
    response.assert_updated()

    response = confd.devices(device['id']).get()
    assert_that(response.item, has_entries(mac=none(),
                                           template_id=none(),
                                           status='not_configured',
                                           plugin=none(),
                                           vendor=none(),
                                           version=none(),
                                           description=none(),
                                           options=none()))


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
