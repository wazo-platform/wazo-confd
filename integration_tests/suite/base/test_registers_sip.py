# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    none,
    not_,
)

from ..helpers import scenarios as s
from ..helpers import fixtures
from . import confd


def test_get_errors():
    fake_register_sip = confd.registers.sip(999999).get
    s.check_resource_not_found(fake_register_sip, 'SIPRegister')


def test_delete_errors():
    fake_register_sip = confd.registers.sip(999999).delete
    s.check_resource_not_found(fake_register_sip, 'SIPRegister')


def test_post_errors():
    url = confd.registers.sip.post
    error_checks(url)


@fixtures.register_sip()
def test_put_errors(register_sip):
    url = confd.registers.sip(register_sip['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'transport', 'invalid')
    s.check_bogus_field_returns_error(url, 'transport', 123)
    s.check_bogus_field_returns_error(url, 'transport', True)
    s.check_bogus_field_returns_error(url, 'transport', [])
    s.check_bogus_field_returns_error(url, 'transport', {})
    s.check_bogus_field_returns_error(url, 'sip_username', ':')
    s.check_bogus_field_returns_error(url, 'sip_username', '/')
    s.check_bogus_field_returns_error(url, 'sip_username', 'value with space')
    s.check_bogus_field_returns_error(url, 'sip_username', 123)
    s.check_bogus_field_returns_error(url, 'sip_username', True)
    s.check_bogus_field_returns_error(url, 'sip_username', [])
    s.check_bogus_field_returns_error(url, 'sip_username', {})
    s.check_bogus_field_returns_error(url, 'auth_password', ':')
    s.check_bogus_field_returns_error(url, 'auth_password', '/')
    s.check_bogus_field_returns_error(url, 'auth_password', 'value with space')
    s.check_bogus_field_returns_error(url, 'auth_password', 123)
    s.check_bogus_field_returns_error(url, 'auth_password', True)
    s.check_bogus_field_returns_error(url, 'auth_password', [])
    s.check_bogus_field_returns_error(url, 'auth_password', {})
    s.check_bogus_field_returns_error(url, 'auth_username', ':')
    s.check_bogus_field_returns_error(url, 'auth_username', '/')
    s.check_bogus_field_returns_error(url, 'auth_username', 'value with space')
    s.check_bogus_field_returns_error(url, 'auth_username', 123)
    s.check_bogus_field_returns_error(url, 'auth_username', True)
    s.check_bogus_field_returns_error(url, 'auth_username', [])
    s.check_bogus_field_returns_error(url, 'auth_username', {})
    s.check_bogus_field_returns_error(url, 'remote_host', ':')
    s.check_bogus_field_returns_error(url, 'remote_host', '/')
    s.check_bogus_field_returns_error(url, 'remote_host', '~')
    s.check_bogus_field_returns_error(url, 'remote_host', 'value with space')
    s.check_bogus_field_returns_error(url, 'remote_host', 123)
    s.check_bogus_field_returns_error(url, 'remote_host', True)
    s.check_bogus_field_returns_error(url, 'remote_host', [])
    s.check_bogus_field_returns_error(url, 'remote_host', {})
    s.check_bogus_field_returns_error(url, 'remote_port', 'invalid')
    s.check_bogus_field_returns_error(url, 'remote_port', [])
    s.check_bogus_field_returns_error(url, 'remote_port', {})
    s.check_bogus_field_returns_error(url, 'callback_extension', '~')
    s.check_bogus_field_returns_error(url, 'callback_extension', 'value with space')
    s.check_bogus_field_returns_error(url, 'callback_extension', 123)
    s.check_bogus_field_returns_error(url, 'callback_extension', True)
    s.check_bogus_field_returns_error(url, 'callback_extension', [])
    s.check_bogus_field_returns_error(url, 'callback_extension', {})
    s.check_bogus_field_returns_error(url, 'expiration', 'invalid')
    s.check_bogus_field_returns_error(url, 'expiration', [])
    s.check_bogus_field_returns_error(url, 'expiration', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'string')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])


@fixtures.register_sip()
def test_get(register_sip):
    response = confd.registers.sip(register_sip['id']).get()
    assert_that(response.item, has_entries(
        id=register_sip['id'],
        transport=none(),
        sip_username=register_sip['sip_username'],
        auth_password=none(),
        auth_username=none(),
        remote_host=register_sip['remote_host'],
        remote_port=none(),
        callback_extension=none(),
        expiration=none(),
        enabled=True,
        trunk=none(),
    ))


def test_create_minimal_parameters():
    response = confd.registers.sip.post(sip_username='sip-username', remote_host='remote-host')
    response.assert_created('register_sip', location='registers/sip')

    assert_that(response.item, has_entries(
        id=not_(empty()),
        sip_username='sip-username',
        remote_host='remote-host',
    ))


def test_create_all_parameters():
    parameters = dict(
        transport='tcp',
        sip_username='sip-username',
        auth_password='auth-password',
        auth_username='auth-username',
        remote_host='remote-host',
        remote_port=1234,
        callback_extension='callback-extension',
        expiration=1000,
        enabled=True
    )
    response = confd.registers.sip.post(**parameters)

    response.assert_created('register_sip', location='registers/sip')
    assert_that(response.item, has_entries(id=not_(empty()), **parameters))


@fixtures.register_sip()
def test_edit_minimal_parameters(register_sip):
    parameters = {}

    response = confd.registers.sip(register_sip['id']).put(**parameters)
    response.assert_updated()


@fixtures.register_sip()
def test_edit_all_parameters(register_sip):
    parameters = dict(
        transport='tcp',
        sip_username='sip-username',
        auth_password='auth-password',
        auth_username='auth-username',
        remote_host='remote-host',
        remote_port=1234,
        callback_extension='callback-extension',
        expiration=1000,
        enabled=False
    )

    response = confd.registers.sip(register_sip['id']).put(**parameters)
    response.assert_updated()

    response = confd.registers.sip(register_sip['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.register_sip()
def test_delete(register_sip):
    response = confd.registers.sip(register_sip['id']).delete()
    response.assert_deleted()


@fixtures.register_sip()
def test_bus_events(register_sip):
    s.check_bus_event(
        'config.register.sip.created',
        confd.registers.sip.post,
        {'sip_username': 'bus-event', 'remote_host': 'bus-event'}
    )
    s.check_bus_event('config.register.sip.edited', confd.registers.sip(register_sip['id']).put)
    s.check_bus_event('config.register.sip.deleted', confd.registers.sip(register_sip['id']).delete)
