# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from datetime import datetime

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_key,
    is_not,
    none,
    not_none,
    starts_with,
    all_of,
    not_,
    has_items,
)

from . import confd, mocks, provd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


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

        device_id = response.json['id']
        device = self.provd.devices.get(device_id)
        config = self.provd.configs.get(device['config'])
        self.provd.assert_device_has_autoprov_config(device)
        self.provd.assert_config_use_device_template(config, self.template_id)
        self.provd.assert_config_does_not_exist(device_id)


def test_search_errors():
    url = confd.devices.get
    s.search_error_checks(url)


def test_get_errors():
    fake_get = confd.devices(999999).get
    s.check_resource_not_found(fake_get, 'Device')


def test_post_errors():
    url = confd.devices.post
    error_checks(url)


def test_put_errors():
    with fixtures.device() as device:
        url = confd.devices(device['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'ip', 123)
    s.check_bogus_field_returns_error(url, 'ip', 'abcd1234')
    s.check_bogus_field_returns_error(url, 'mac', 123)
    s.check_bogus_field_returns_error(url, 'mac', 'abcd1234')
    s.check_bogus_field_returns_error(url, 'mac', 'abcd1234')
    s.check_bogus_field_returns_error(url, 'plugin', 'invalidplugin')
    s.check_bogus_field_returns_error(url, 'template_id', 'invalidtemplateid')
    s.check_bogus_field_returns_error(url, 'options', 'invalidoption')
    s.check_bogus_field_returns_error(url, 'options', {'switchboard': 'yes'})


def test_search():
    with fixtures.device(
    ip="10.20.30.40",
    mac="aa:bb:aa:cc:01:23",
    model="SearchModel",
    plugin='zero',
    sn="SearchSn",
    vendor='SearchVendor',
    version='1.0',
    description='SearchDesc',
) as device, fixtures.device(
    ip="11.22.33.44",
    mac="dd:ee:dd:ff:45:67",
    model="HiddenModel",
    plugin='null',
    sn="HiddenSn",
    vendor="HiddenVendor",
    version="2.0",
    description="HiddenDesc",
) as hidden:
        url = confd.devices
        searches = {
            'ip': '20.30',
            'mac': 'bb:aa',
            'model': 'chmod',
            'plugin': 'zer',
            'sn': 'chsn',
            'vendor': 'chven',
            'version': '1.0',
            'description': 'rchdes',
        }

        for field, term in searches.items():
            check_search(url, device, hidden, field, term)



def check_search(url, device, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, device[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: device[field]})
    assert_that(response.items, has_item(has_entry('id', device['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.devices.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.devices.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_list_unallocated():
    with fixtures.device() as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices.unallocated.get()
        assert_that(
            response.items,
            all_of(has_item(main), not_(has_item(sub))),
        )

        response = confd.devices.unallocated.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main), not_(has_item(sub))),
        )



def test_sorting_offset_limit():
    with fixtures.device(
    ip="99.20.30.40",
    mac="aa:bb:aa:cc:01:23",
    model="SortModel1",
    sn="SortSn1",
    vendor='SortVendor1',
    version='1.0',
    description='SortDesc1',
) as device1, fixtures.device(
    ip="99.21.30.40",
    mac="bb:cc:dd:aa:bb:cc",
    model="SortModel2",
    sn="SortSn2",
    vendor="SortVendor2",
    version="1.1",
    description="SortDesc2",
) as device2:
        url = confd.devices.get
        s.check_sorting(url, device1, device2, 'ip', '99.')
        s.check_sorting(url, device1, device2, 'model', 'SortModel')
        s.check_sorting(url, device1, device2, 'sn', 'SortSn')
        s.check_sorting(url, device1, device2, 'vendor', 'SortVendor')
        s.check_sorting(url, device1, device2, 'version', '1.')
        s.check_sorting(url, device1, device2, 'description', 'SortDesc')

        s.check_offset(url, device1, device2, 'mac', 'aa:bb')
        s.check_offset_legacy(url, device1, device2, 'mac', 'aa:bb')

        s.check_limit(url, device1, device2, 'mac', 'aa:bb')



def test_get():
    with fixtures.device() as device:
        response = confd.devices(device['id']).get()
        assert_that(response.item, has_entries(**device))



def test_get_multi_tenant():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))

        response = confd.devices(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Device'))



def test_create_device_minimal_parameters():
    response = confd.devices.post()
    response.assert_created('devices')

    assert_that(
        response.item,
        has_entries(
            mac=none(),
            template_id=none(),
            status='not_configured',
            plugin=none(),
            vendor=none(),
            version=none(),
            description=none(),
            options=none(),
        )
    )

    provd_device = provd.devices.get(response.item['id'])
    assert_that(provd_device['config'], starts_with('autoprov'))


def test_create_device_multi_tenant():
    response = confd.devices.post(wazo_tenant=SUB_TENANT)
    response.assert_created('devices')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


def test_create_device_null_parameters():
    response = confd.devices.post(
        mac=None,
        template_id=None,
        plugin=None,
        vendor=None,
        version=None,
        description=None,
        options=None,
    )
    response.assert_created('devices')

    assert_that(
        response.item,
        has_entries(
            mac=none(),
            template_id=none(),
            status='not_configured',
            plugin=none(),
            vendor=none(),
            version=none(),
            description=none(),
            options=none(),
        )
    )

    provd_device = provd.devices.get(response.item['id'])
    assert_that(provd_device['config'], starts_with('autoprov'))


def test_create_device_all_parameters():
    mac, ip = h.device.generate_mac_and_ip()
    template_config = provd.configs.list({'id': 'mockdevicetemplate'})['configs'][0]

    parameters = {
        'ip': ip,
        'mac': mac,
        'model': '6731i',
        'plugin': 'null',
        'sn': 'sn',
        'template_id': 'mockdevicetemplate',
        'vendor': 'Aastra',
        'version': '1.0',
        'description': 'mydevice',
        'options': {'switchboard': True},
    }

    response = confd.devices.post(**parameters)
    response.assert_created('devices')
    assert_that(response.item, has_entries(parameters))

    provd_device = provd.devices.get(response.item['id'])
    assert_that(
        provd_device,
        has_entries({
            'ip': ip,
            'mac': mac,
            'model': '6731i',
            'plugin': 'null',
            'sn': 'sn',
            'vendor': 'Aastra',
            'version': '1.0',
            'description': 'mydevice',
            'options': {'switchboard': True}},
        )
    )

    provd_config = provd.configs.get(provd_device['config'])
    assert_that(provd_config['id'], starts_with('autoprov'))
    assert_that(provd_config['parent_ids'], has_item(template_config['id']))


def test_create_2_devices_with_same_mac():
    with fixtures.device() as device:
        response = confd.devices.post(mac=device['mac'])
        response.assert_match(400, e.resource_exists('Device'))



def test_create_2_devices_with_same_mac_different_tenants():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as device:
        response = confd.devices.post(mac=device['mac'], wazo_tenant=SUB_TENANT)
        response.assert_match(400, e.resource_exists('Device'))



def test_create_2_devices_with_same_ip():
    with fixtures.device() as device:
        response = confd.devices.post(ip=device['ip'])
        response.assert_created('devices')



def test_create_2_devices_with_same_ip_different_tenants():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as device:
        response = confd.devices.post(ip=device['ip'], wazo_tenant=SUB_TENANT)
        response.assert_created('devices')



def test_create_device_with_fake_plugin():
    response = confd.devices.post(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


def test_create_device_with_fake_template():
    response = confd.devices.post(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


def test_edit_device_all_parameters():
    with fixtures.device(plugin='zero', template_id='defaultconfigdevice') as device:
        mac, ip = h.device.generate_mac_and_ip()
        parameters = {
            'ip': ip,
            'mac': mac,
            'model': '6731i',
            'plugin': 'null',
            'sn': 'sn',
            'template_id': 'mockdevicetemplate',
            'vendor': 'Aastra',
            'version': '1.0',
            'description': 'mydevice',
            'options': {'switchboard': True},
        }

        response = confd.devices(device['id']).put(**parameters)
        response.assert_updated()

        response = confd.devices(device['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_device_multi_tenant():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Device'))

        response = confd.devices(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_change_tenant_unallocated():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main:
        response = confd.devices.unallocated(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_updated()

        response = confd.devices(main['id']).get(wazo_tenant=SUB_TENANT)
        assert_that(response.item, has_entries(id=main['id']))

        response = confd.devices.unallocated(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Device'))



def test_edit_device_null_parameters():
    with fixtures.device(
    ip="127.8.0.8",
    mac="a1:b1:c1:d1:e1:f1",
    model='6731i',
    plugin='zero',
    sn='sn',
    template_id='defaultconfigdevice',
    vendor='1.0',
    description='nullparameters',
    options={'switchboard': True},
) as device:
        url = confd.devices(device['id'])
        response = url.put(
            mac=None,
            template_id=None,
            plugin=None,
            vendor=None,
            version=None,
            description=None,
            options=None,
        )
        response.assert_updated()

        response = confd.devices(device['id']).get()
        assert_that(
            response.item,
            has_entries(
                mac=none(),
                template_id=none(),
                status='not_configured',
                plugin=none(),
                vendor=none(),
                version=none(),
                description=none(),
                options=none(),
            )
        )



def test_edit_device_with_same_mac():
    with fixtures.device() as first_device, fixtures.device() as second_device:
        response = confd.devices(first_device['id']).put(mac=second_device['mac'])
        response.assert_match(400, e.resource_exists('Device'))



def test_edit_device_with_same_mac_different_tenants():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as first_device, fixtures.device(wazo_tenant=SUB_TENANT) as second_device:
        response = confd.devices(first_device['id']).put(mac=second_device['mac'], wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.resource_exists('Device'))



def test_edit_device_with_fake_plugin():
    with fixtures.device() as device:
        response = confd.devices(device['id']).put(plugin='superduperplugin')
        response.assert_match(400, e.not_found('Plugin'))



def test_edit_device_with_fake_template():
    with fixtures.device() as device:
        response = confd.devices(device['id']).put(template_id='superdupertemplate')
        response.assert_match(400, e.not_found('DeviceTemplate'))



def test_delete_device():
    with fixtures.device() as device:
        response = confd.devices(device['id']).delete()
        response.assert_deleted()

        provd_devices = provd.devices.list({'id': device['id']})['devices']
        assert_that(provd_devices, empty())



def test_delete_device_multi_tenant():
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Device'))

        response = confd.devices(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()

        params = {'id': sub['id']}
        provd_devices = provd.devices.list(params, tenant_uuid=MAIN_TENANT, recurse=True)['devices']
        assert_that(provd_devices, empty())



@mocks.provd()
def test_reset_to_autoprov_device_associated_to_line(provd):
    with fixtures.device() as device, fixtures.line() as line:
        with a.line_device(line, device, check=False):
            response = confd.devices(device['id']).autoprov.get()
            response.assert_ok()

            device_cfg = provd.devices.get(device['id'])
            assert_that(device_cfg, has_entries(config=starts_with('autoprov')))
            assert_that(device_cfg, is_not(has_key('options')))

            config_cfg = provd.configs.get(device_cfg['config'])
            assert_that(config_cfg, not_none())

            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries(device_id=none()))


@mocks.provd()
def test_reset_to_autoprov_multi_tenant(provd):
    with fixtures.context(name='main_ctx', wazo_tenant=MAIN_TENANT) as _, fixtures.context(name='sub_ctx', wazo_tenant=SUB_TENANT) as __, fixtures.device(wazo_tenant=MAIN_TENANT) as main_device, fixtures.device(wazo_tenant=SUB_TENANT) as sub_device, fixtures.line(context='main_ctx') as main_line, fixtures.line(context='sub_ctx') as sub_line:
        with a.line_device(main_line, main_device, check=False) \
            and a.line_device(sub_line, sub_device, check=False):
            response = confd.devices(main_device['id']).autoprov.get(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('Device'))

            response = confd.devices(sub_device['id']).autoprov.get(wazo_tenant=MAIN_TENANT)
            response.assert_ok()

            device_cfg = provd.devices.get(sub_device['id'])
            assert_that(device_cfg, has_entries(config=starts_with('autoprov')))
            assert_that(device_cfg, is_not(has_key('options')))

            config_cfg = provd.configs.get(device_cfg['config'])
            assert_that(config_cfg, not_none())

            response = confd.lines(sub_line['id']).get(wazo_tenant=MAIN_TENANT)
            assert_that(response.item, has_entries(device_id=none()))


@mocks.provd()
def test_synchronize_device(provd):
    with fixtures.device() as device:
        timestamp = datetime.utcnow()

        response = confd.devices(device['id']).synchronize.get()
        response.assert_ok()

        synchonized = provd.has_synchronized(device['id'], timestamp)
        assert_that(synchonized, "Device was not synchronized")



@mocks.provd()
def test_synchronize_device_multi_tenant(provd):
    with fixtures.device(wazo_tenant=MAIN_TENANT) as main, fixtures.device(wazo_tenant=SUB_TENANT) as sub:
        response = confd.devices(main['id']).synchronize.get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Device'))

        timestamp = datetime.utcnow()

        response = confd.devices(sub['id']).synchronize.get(wazo_tenant=MAIN_TENANT)
        response.assert_ok()

        synchonized = provd.has_synchronized(sub['id'], timestamp)
        assert_that(synchonized, "Device was not synchronized")

