# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from contextlib import contextmanager

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_entries,
    has_items,
    is_,
    is_not,
    none,
    not_,
    starts_with,
)

from . import confd, db, provd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT as DEFAULT_DEVICE_TENANT,
    MAIN_TENANT,
    SUB_TENANT,
)
from ..helpers.helpers.line_fellowship import line_fellowship


@contextmanager
def line_and_device(endpoint_type='sip', wazo_tenant=None):
    device = h.device.generate_device(wazo_tenant=wazo_tenant)

    line_etc = line_fellowship(endpoint_type=endpoint_type, wazo_tenant=wazo_tenant)
    with line_etc as (user, line, extension, endpoint):
        yield line, device

    h.device.delete_device(device['id'])


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


@fixtures.sip()
@fixtures.sccp()
def test_associate_without_required_resources_raises_error(sip, sccp):
    yield check_associate_without_required_resources, sip, a.line_endpoint_sip
    yield check_associate_without_required_resources, sccp, a.line_endpoint_sccp


def check_associate_without_required_resources(endpoint, line_endpoint):
    error = e.missing_association()

    with fixtures.user() as user, fixtures.line() as line, fixtures.extension() as extension, fixtures.device() as device:

        url = confd.lines(line['id']).devices(device['id'])
        url.put().assert_match(400, error)
        with line_endpoint(line, endpoint):
            url.put().assert_match(400, error)
            with a.line_extension(line, extension):
                url.put().assert_match(400, error)
                with a.user_line(user, line):
                    url.put().assert_updated()
                    url.delete()


@fixtures.line(position=1)
def test_associate_2_lines_with_same_position_raises_error(extra_line):
    with line_and_device('sip') as (line, device):
        yield check_2_lines_with_same_position_raises_error, line, extra_line, device

    with line_and_device('sccp') as (line, device):
        yield check_2_lines_with_same_position_raises_error, line, extra_line, device


def check_2_lines_with_same_position_raises_error(line, extra_line, device):
    response = confd.lines(line['id']).devices(device['id']).put()
    response.assert_ok()

    response = confd.lines(extra_line['id']).devices(device['id']).put()
    response.assert_match(
        400, re.compile("Cannot associate 2 lines with same position")
    )


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
        assert_that(
            response.item, has_entries(line_id=line['id'], device_id=device['id'])
        )


def test_get_device_associated_to_line_from_sub_tenant_errors():
    with line_and_device('sip', wazo_tenant=MAIN_TENANT) as (
        line,
        device,
    ), a.line_device(line, device):
        response = confd.lines(line['id']).devices.get(wazo_tenant=SUB_TENANT)
        response.assert_status(404)

    with line_and_device('sccp', wazo_tenant=MAIN_TENANT) as (
        line,
        device,
    ), a.line_device(line, device):
        response = confd.lines(line['id']).devices.get(wazo_tenant=SUB_TENANT)
        response.assert_status(404)


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

    with a.line_device(line, device):
        response = confd.devices(device['id']).lines.get()
        assert_that(
            response.items,
            contains(has_entries(line_id=line['id'], device_id=device['id'])),
        )


def test_get_line_associated_to_a_device_from_sub_tenant_errors():
    with line_and_device('sip', wazo_tenant=MAIN_TENANT) as (
        line,
        device,
    ), a.line_device(line, device):
        response = confd.devices(device['id']).lines.get(wazo_tenant=SUB_TENANT)
        response.assert_status(404)

    with line_and_device('sccp', wazo_tenant=MAIN_TENANT) as (
        line,
        device,
    ), a.line_device(line, device):
        response = confd.devices(device['id']).lines.get(wazo_tenant=SUB_TENANT)
        response.assert_status(404)


def assert_provd_config(user, line, provd_config):
    assert_that(
        provd_config,
        has_entries(
            id=is_not(starts_with('autoprov')),
            configdevice='defaultconfigdevice',
            deletable=True,
            parent_ids=has_items('base', 'defaultconfigdevice'),
            raw_config=has_entries(
                X_key='',
                config_version=1,
                X_xivo_user_uuid=user['uuid'],
                X_xivo_phonebook_profile=line['context'],
                exten_dnd='*25',
                exten_fwd_unconditional='*21',
                exten_fwd_no_answer='*22',
                exten_fwd_busy='*23',
                exten_fwd_disable_all='*20',
                exten_pickup_call='*8',
                exten_voicemail='*98',
                exten_park=none(),
                exten_pickup_group=none(),
            ),
        ),
    )


def assert_sip_config(user, sip, extension, provd_config, position=1):
    position = str(position)
    fullname = "{u[firstname]} {u[lastname]}".format(u=user)
    registrar = confd.registrars('default').get().item
    username, password = None, None
    for key, value in sip['auth_section_options']:
        if key == 'username':
            username = value
        elif key == 'password':
            password = value

    assert_that(
        provd_config['raw_config'],
        has_entries(
            protocol='SIP',
            sip_lines=has_entries(
                {
                    position: has_entries(
                        auth_username=username,
                        username=username,
                        password=password,
                        display_name=fullname,
                        number=extension['exten'],
                        proxy_ip=registrar['proxy_main_host'],
                        registrar_ip=registrar['main_host'],
                        backup_proxy_ip=registrar['proxy_backup_host'],
                        backup_registrar_ip=registrar['backup_host'],
                    )
                }
            ),
        ),
    )


def assert_sccp_config(provd_config):
    registrar = confd.registrars('default').get().item

    assert_that(
        provd_config['raw_config'],
        has_entries(
            protocol='SCCP',
            sccp_call_managers=has_entries(
                {
                    '1': has_entries(ip=registrar['proxy_main_host']),
                    '2': has_entries(ip=registrar['proxy_backup_host']),
                }
            ),
        ),
    )


@fixtures.device()
def test_associate_sip_line(device):
    registrar = confd.registrars('default').get().item
    registrar['proxy_backup_host'] = '127.0.0.2'
    registrar['backup_host'] = '127.0.0.2'
    confd.registrars(registrar['id']).put(registrar)

    with line_fellowship('sip', generate_username_password=True) as (
        user,
        line,
        extension,
        sip,
    ):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        device_config = provd.devices.get(device['id'])
        assert_that(device_config['config'], is_not(starts_with('autoprov')))

        provd_config = provd.configs.get(device['id'])
        assert_provd_config(user, line, provd_config)
        assert_sip_config(user, sip, extension, provd_config)


@fixtures.device(wazo_tenant=DEFAULT_DEVICE_TENANT)
def test_associate_sip_line_change_tenant(device):
    registrar = confd.registrars('default').get().item
    registrar['proxy_backup_host'] = '127.0.0.2'
    registrar['backup_host'] = '127.0.0.2'
    confd.registrars(registrar['id']).put(registrar)

    with line_fellowship(
        'sip', generate_username_password=True, wazo_tenant=SUB_TENANT
    ) as (user, line, extension, sip):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        device_config = provd.devices.get(device['id'])
        assert_that(device_config['tenant_uuid'], is_(SUB_TENANT))


@fixtures.device()
def test_associate_2_sip_lines(device):
    registrar = confd.registrars('default').get().item
    registrar['proxy_backup_host'] = '127.0.0.2'
    registrar['backup_host'] = '127.0.0.2'
    confd.registrars(registrar['id']).put(registrar).assert_updated()

    with line_fellowship('sip', generate_username_password=True) as (
        user1,
        line1,
        extension1,
        sip1,
    ), line_fellowship('sip', generate_username_password=True) as (
        user2,
        line2,
        extension2,
        sip2,
    ):

        confd.lines(line2['id']).put(position=2).assert_updated()
        confd.lines(line1['id']).devices(device['id']).put().assert_updated()
        confd.lines(line2['id']).devices(device['id']).put().assert_updated()

        provd_config = provd.configs.get(device['id'])
        assert_provd_config(user1, line1, provd_config)
        assert_sip_config(user1, sip1, extension1, provd_config, position=1)
        assert_sip_config(user2, sip2, extension2, provd_config, position=2)


@fixtures.device(wazo_tenant=MAIN_TENANT)
@fixtures.device(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_device, sub_device):
    with line_fellowship(
        'sip', generate_username_password=True, wazo_tenant=MAIN_TENANT
    ) as (
        user,
        main_line,
        extension,
        sip,
    ):
        response = (
            confd.lines(main_line['id'])
            .devices(sub_device['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

    with line_fellowship(
        'sip', generate_username_password=True, wazo_tenant=SUB_TENANT
    ) as (
        user,
        sub_line,
        extension,
        sip,
    ):
        response = (
            confd.lines(sub_line['id'])
            .devices(main_device['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Device'))

    with line_fellowship('sip', wazo_tenant=MAIN_TENANT) as (
        user,
        main_line,
        extension,
        sip,
    ):
        response = (
            confd.lines(main_line['id'])
            .devices(sub_device['id'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())


@fixtures.device()
def test_associate_2_sccp_lines(device):
    with line_fellowship('sccp') as (user1, line1, extension1, sccp1), line_fellowship(
        'sccp'
    ) as (user2, line2, extension2, sccp2):

        confd.lines(line2['id']).put(position=2).assert_updated()
        confd.lines(line1['id']).devices(device['id']).put().assert_updated()

        response = confd.lines(line2['id']).devices(device['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


@fixtures.device()
def test_associate_lines_with_different_endpoints(device):
    with line_fellowship('sip', generate_username_password=True) as (
        user1,
        line1,
        extension1,
        sip,
    ), line_fellowship('sccp') as (user2, line2, extension2, sccp):

        confd.lines(line2['id']).put(position=2).assert_updated()
        confd.lines(line1['id']).devices(device['id']).put().assert_updated()

        response = confd.lines(line2['id']).devices(device['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


def assert_sccp_in_db(line, device):
    sccp_device = 'SEP' + device['mac'].replace(':', '').upper()
    with db.queries() as q:
        assert_that(q.line_has_sccp_device(line['id'], sccp_device))


@fixtures.device()
def test_associate_sccp_line(device):
    registrar = confd.registrars('default').get().item
    registrar['proxy_backup_host'] = '127.0.0.2'
    confd.registrars(registrar['id']).put(registrar)

    with line_fellowship('sccp') as (user, line, extension, sccp):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        device_config = provd.devices.get(device['id'])
        assert_that(device_config['config'], is_not(starts_with('autoprov')))

        provd_config = provd.configs.get(device['id'])
        assert_provd_config(user, line, provd_config)
        assert_sccp_config(provd_config)
        assert_sccp_in_db(line, device)


@fixtures.device(wazo_tenant=DEFAULT_DEVICE_TENANT)
def test_associate_sccp_line_change_tenant(device):
    registrar = confd.registrars('default').get().item
    registrar['proxy_backup_host'] = '127.0.0.2'
    confd.registrars(registrar['id']).put(registrar)

    with line_fellowship('sccp', wazo_tenant=SUB_TENANT) as (
        user,
        line,
        extension,
        sccp,
    ):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_updated()

        device_config = provd.devices.get(device['id'], wazo_tenant=SUB_TENANT)
        assert_that(device_config['tenant_uuid'], is_(SUB_TENANT))


def test_associate_when_device_already_associated():
    with line_and_device('sip') as (line, device):
        with a.line_device(line, device):
            response = confd.lines(line['id']).devices(device['id']).put()
            response.assert_updated()

    with line_and_device('sccp') as (line, device):
        with a.line_device(line, device):
            response = confd.lines(line['id']).devices(device['id']).put()
            response.assert_updated()


def test_associate_with_another_device_when_already_associated():
    device2 = h.device.generate_device()

    with line_and_device('sip') as (line, device1):
        with a.line_device(line, device1):
            response = confd.lines(line['id']).devices(device2['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Device'))

    with line_and_device('sccp') as (line, device1):
        with a.line_device(line, device1):
            response = confd.lines(line['id']).devices(device2['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Device'))


def test_dissociate():
    with line_and_device('sip') as (line, device):
        yield check_dissociate, line, device

    with line_and_device('sccp') as (line, device):
        yield check_dissociate, line, device
        yield check_dissociate_sccp, line, device


def check_dissociate(line, device):
    with a.line_device(line, device, check=False):
        response = confd.lines(line['id']).devices(device['id']).delete()
        response.assert_deleted()

        provd_device = provd.devices.get(device['id'])
        assert_that(provd_device['config'], starts_with('autoprov'))


def check_dissociate_sccp(line, device):
    sccp_device = 'SEP' + device['mac'].replace(":", "").upper()
    with db.queries() as q:
        assert_that(q.line_has_sccp_device(line['id'], sccp_device), equal_to(False))


def test_reset_sccp_to_autoprov():
    with line_and_device('sccp') as (line, device):
        response = confd.lines(line['id']).devices(device['id']).put()
        response.assert_ok()

        confd.devices(device['id']).autoprov.get()
        provd_device = provd.devices.get(device['id'])
        assert_that(provd_device['config'], starts_with('autoprov'))
        yield check_sccp_reset_to_autoprov, device


def check_sccp_reset_to_autoprov(device):
    sccp_device = 'SEP' + device['mac'].replace(":", "").upper()
    with db.queries() as q:
        assert_that(q.sccp_device_exists(sccp_device), equal_to(False))


def test_dissociate_multi_tenant():
    with line_and_device('sip', wazo_tenant=MAIN_TENANT) as (
        main_line,
        main_device,
    ), line_and_device('sip', wazo_tenant=SUB_TENANT) as (sub_line, sub_device):
        response = (
            confd.lines(main_line['id'])
            .devices(sub_device['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.lines(sub_line['id'])
            .devices(main_device['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Device'))


def test_dissociate_when_not_associated():
    with line_and_device('sip') as (line1, device1), line_and_device('sip') as (
        line2,
        device2,
    ):
        yield check_dissociate_when_not_associated, line1, device1, line2, device2

    with line_and_device('sccp') as (line1, device1), line_and_device('sccp') as (
        line2,
        device2,
    ):
        yield check_dissociate_when_not_associated, line1, device1, line2, device2


def check_dissociate_when_not_associated(line1, device1, line2, device2):
    with a.line_device(line1, device1), a.line_device(line2, device2):
        response = confd.lines(line1['id']).devices(device2['id']).delete()
        response.assert_deleted()

        provd_device1 = provd.devices.get(device1['id'])
        assert_that(provd_device1['config'], not_(starts_with('autoprov')))

        provd_device2 = provd.devices.get(device2['id'])
        assert_that(provd_device2['config'], not_(starts_with('autoprov')))

        response = confd.lines(line1['id']).get()
        assert_that(response.item, has_entries(device_id=device1['id']))

        response = confd.lines(line2['id']).get()
        assert_that(response.item, has_entries(device_id=device2['id']))


@fixtures.device()
def test_bus_events(device):
    with line_fellowship('sip') as (user, line, extension, sip):
        associate_url = confd.lines(line['id']).devices(device['id']).put
        routing_key = 'config.lines.{}.devices.{}.updated'.format(
            line['id'], device['id']
        )
        yield s.check_bus_event, routing_key, associate_url

        dissociate_url = confd.lines(line['id']).devices(device['id']).delete
        routing_key = 'config.lines.{}.devices.{}.deleted'.format(
            line['id'], device['id']
        )
        yield s.check_bus_event, routing_key, dissociate_url
