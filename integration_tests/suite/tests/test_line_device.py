# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from contextlib import contextmanager

from hamcrest import assert_that, has_entries, is_not, starts_with, has_key, equal_to, contains

from test_api import scenarios as s
from test_api import confd
from test_api import provd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a
from test_api import helpers as h


@contextmanager
def line_fellowship(endpoint_type='sip'):
    user = h.user.generate_user()
    line = h.line.generate_line()
    extension = h.extension.generate_extension()

    if endpoint_type == 'sip':
        endpoint = h.endpoint_sip.generate_sip()
        line_endpoint = h.line_endpoint_sip
    else:
        endpoint = h.endpoint_sccp.generate_sccp()
        line_endpoint = h.line_endpoint_sccp

    line_endpoint.associate(line['id'], endpoint['id'])
    h.user_line.associate(user['id'], line['id'])
    h.line_extension.associate(line['id'], extension['id'])

    yield user, line, extension, endpoint

    h.line_extension.dissociate(line['id'], extension['id'], False)
    h.user_line.dissociate(user['id'], line['id'], False)
    line_endpoint.dissociate(line['id'], endpoint['id'], False)

    if endpoint_type == 'sip':
        h.endpoint_sip.delete_sip(endpoint['id'])
    else:
        h.endpoint_sccp.delete_sccp(endpoint['id'])

    h.user.delete_user(user['id'])
    h.line.delete_line(line['id'])
    h.extension.delete_extension(extension['id'])


@contextmanager
def line_and_device(endpoint_type='sip'):
    device = h.device.generate_device()

    with line_fellowship(endpoint_type) as (user, line, extension, endpoint):
        yield line, device

    h.device.delete_device(device)


@fixtures.line()
@fixtures.device()
def test_associate_errors(line, device):
    fake_line = confd.lines(999999999).devices(device['id']).put
    fake_device = confd.lines(line['id']).devices(999999999).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_device, 'Device'


@fixtures.line()
@fixtures.device()
def test_dissociate_errors(line, device):
    fake_line = confd.lines(999999999).devices(device['id']).delete
    fake_device = confd.lines(line['id']).devices(999999999).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_device, 'Device'


def test_get_errors():
    fake_line = confd.lines(999999999).devices.get
    fake_device = confd.devices(999999999).lines.get

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_device, 'Device'


def test_get_device_associated_to_line():
    with line_and_device('sip') as (line, device):
        yield check_get_device_associated_to_line, line, device

    with line_and_device('sccp') as (line, device):
        yield check_get_device_associated_to_line, line, device


def check_get_device_associated_to_line(line, device):
    response = confd.lines(line['id']).devices.get()
    response.assert_status(404)

    with a.line_device(line, device):
        response = confd.lines(line['id']).devices.get()
        assert_that(response.item, has_entries(line_id=line['id'],
                                               device_id=device['id']))


def test_get_device_after_dissociation():
    with line_and_device('sip') as (line, device):
        yield check_get_device_after_dissociation, line, device

    with line_and_device('sccp') as (line, device):
        yield check_get_device_after_dissociation, line, device


def check_get_device_after_dissociation(line, device):
    h.line_device.associate(line['id'], device['id'])
    h.line_device.dissociate(line['id'], device['id'])

    response = confd.lines(line['id']).devices.get()
    response.assert_status(404)


def test_get_line_associated_to_a_device():
    with line_and_device('sip') as (line, device):
        yield check_get_line_associated_to_a_device, line, device

    with line_and_device('sccp') as (line, device):
        yield check_get_line_associated_to_a_device, line, device


def check_get_line_associated_to_a_device(line, device):
    response = confd.devices(device['id']).lines.get()
    assert_that(response.total, equal_to(0))

    expected = contains(has_entries(line_id=line['id'],
                                    device_id=device['id']))

    with a.line_device(line, device):
        response = confd.devices(device['id']).lines.get()
        assert_that(response.items, expected)


def test_registrar_addresses_without_backup_on_sip_device():
    provd.reset()
    registrar = provd.configs.get('default')

    with line_and_device('sip') as (line, device), a.line_device(line, device):
        config = provd.configs.get(device['id'])
        sip_config = config['raw_config']['sip_lines']['1']

        assert_that(sip_config, has_entries(
            proxy_ip=registrar['proxy_main'],
            registrar_ip=registrar['registrar_main']
        ))

        assert_that(sip_config, is_not(has_key('backup_proxy_ip')))
        assert_that(sip_config, is_not(has_key('backup_registrar_ip')))


def check_registrar_addresses_without_backup_on_sccp_device():
    provd.reset()
    registrar = provd.configs.get('default')

    with line_and_device('sccp') as (line, device), a.line_device(line, device):
        config = provd.configs.get(device['id'])
        sccp_config = config['raw_config']['sccp_call_managers']

        assert_that(sccp_config, has_entries(
            {'1': has_entries(
                ip=registrar['proxy_main']
            )}
        ))

        assert_that(sccp_config, is_not(has_key('2')))


@fixtures.device()
def test_associate_sip_line(device):
    registrar = provd.configs.get('default')
    registrar['proxy_backup'] = '127.0.0.2'
    registrar['registrar_backup'] = '127.0.0.2'
    provd.configs.update(registrar)

    with line_fellowship('sip') as (user, line, extension, sip):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        fullname = "{u[firstname]} {u[lastname]}".format(u=user)
        expected_config = has_entries(auth_username=sip['username'],
                                      username=sip['username'],
                                      password=sip['secret'],
                                      display_name=fullname,
                                      number=extension['exten'],
                                      proxy_ip=registrar['proxy_main'],
                                      registrar_ip=registrar['registrar_main'],
                                      backup_proxy_ip=registrar['proxy_backup'],
                                      backup_registrar_ip=registrar['registrar_backup'])

        provd_config = provd.configs.get(device['id'])
        assert_that(provd_config['id'], is_not(starts_with('autoprov')))
        assert_that(provd_config['raw_config'], has_key('sip_lines'))

        sip_config = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_config, expected_config)


@fixtures.device()
def test_associate_sccp_line(device):
    registrar = provd.configs.get('default')
    registrar['proxy_backup'] = '127.0.0.2'
    provd.configs.update(registrar)

    with line_fellowship('sccp') as (user, line, extension, sccp):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        device_config = provd.devices.get(device['id'])
        assert_that(device_config['config'], is_not(starts_with('autoprov')))

        provd_config = provd.configs.get(device_config['config'])
        assert_that(provd_config['raw_config'], has_key('sccp_call_managers'))

        call_managers = provd_config['raw_config']['sccp_call_managers']
        assert_that(call_managers, has_entries({'1': has_entries(ip=registrar['proxy_main']),
                                                '2': has_entries(ip=registrar['proxy_backup'])
                                                }))


def test_associate_when_device_already_associated():
    with line_and_device('sip') as (line, device):
        yield check_associate_when_device_already_associated, line, device

    with line_and_device('sccp') as (line, device):
        yield check_associate_when_device_already_associated, line, device


def check_associate_when_device_already_associated(line, device):
    with a.line_device(line, device):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


def test_associate_with_another_device_when_already_associated():
    device2 = h.device.generate_device()

    with line_and_device('sip') as (line, device1):
        yield check_associate_with_another_device_when_already_associated, line, device1, device2

    with line_and_device('sccp') as (line, device1):
        yield check_associate_with_another_device_when_already_associated, line, device1, device2


def check_associate_with_another_device_when_already_associated(line, device1, device2):
    with a.line_device(line, device1):
        response = confd.lines(line['id']).devices(device2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


def test_associate_2_lines_to_same_device():
    with line_and_device('sip') as (line1, device), line_fellowship('sip') as (_, line2, _, _):
        yield check_associate_2_lines_to_same_device, line1, line2, device

    with line_and_device('sccp') as (line1, device), line_fellowship('sccp') as (_, line2, _, _):
        yield check_associate_2_lines_to_same_device, line1, line2, device


def check_associate_2_lines_to_same_device(line1, line2, device):
    response = confd.lines(line1['id']).devices(device['id']).put()
    response.assert_updated()

    response = confd.lines(line2['id']).devices(device['id']).put()
    response.assert_updated()


def test_dissociate():
    with line_and_device('sip') as (line, device):
        yield check_dissociate, line, device

    with line_and_device('sccp') as (line, device):
        yield check_dissociate, line, device


def check_dissociate(line, device):
    with a.line_device(line, device, check=False):
        response = confd.lines(line['id']).devices(device['id']).delete()
        response.assert_deleted()

        provd_device = provd.devices.get(device['id'])
        assert_that(provd_device['config'], starts_with('autoprov'))


def test_dissociate_when_not_associated():
    with line_and_device('sip') as (line, device):
        yield check_dissociate_when_not_associated, line, device

    with line_and_device('sccp') as (line, device):
        yield check_dissociate_when_not_associated, line, device


def check_dissociate_when_not_associated(line, device):
    response = confd.lines(line['id']).devices(device['id']).delete()
    response.assert_status(400)
