# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    none,
    not_,
)

from . import confd
from ..helpers import fixtures
from ..helpers import scenarios as s


def test_get_errors():
    fake_register_iax = confd.registers.iax(999999).get
    s.check_resource_not_found(fake_register_iax, 'IAXRegister')


def test_delete_errors():
    fake_register_iax = confd.registers.iax(999999).delete
    s.check_resource_not_found(fake_register_iax, 'IAXRegister')


def test_post_errors():
    url = confd.registers.iax.post
    error_checks(url)


@fixtures.register_iax()
def test_put_errors(register_iax):
    url = confd.registers.iax(register_iax['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'auth_username', ':')
    s.check_bogus_field_returns_error(url, 'auth_username', '/')
    s.check_bogus_field_returns_error(url, 'auth_username', 'value with space')
    s.check_bogus_field_returns_error(url, 'auth_username', 123)
    s.check_bogus_field_returns_error(url, 'auth_username', True)
    s.check_bogus_field_returns_error(url, 'auth_username', [])
    s.check_bogus_field_returns_error(url, 'auth_username', {})
    s.check_bogus_field_returns_error(url, 'auth_password', ':')
    s.check_bogus_field_returns_error(url, 'auth_password', '/')
    s.check_bogus_field_returns_error(url, 'auth_password', 'value with space')
    s.check_bogus_field_returns_error(url, 'auth_password', 123)
    s.check_bogus_field_returns_error(url, 'auth_password', True)
    s.check_bogus_field_returns_error(url, 'auth_password', [])
    s.check_bogus_field_returns_error(url, 'auth_password', {})
    s.check_bogus_field_returns_error(url, 'remote_host', ':')
    s.check_bogus_field_returns_error(url, 'remote_host', '/')
    s.check_bogus_field_returns_error(url, 'remote_host', '?')
    s.check_bogus_field_returns_error(url, 'remote_host', 'value with space')
    s.check_bogus_field_returns_error(url, 'remote_host', 123)
    s.check_bogus_field_returns_error(url, 'remote_host', True)
    s.check_bogus_field_returns_error(url, 'remote_host', [])
    s.check_bogus_field_returns_error(url, 'remote_host', {})
    s.check_bogus_field_returns_error(url, 'remote_port', 'invalid')
    s.check_bogus_field_returns_error(url, 'remote_port', [])
    s.check_bogus_field_returns_error(url, 'remote_port', {})
    s.check_bogus_field_returns_error(url, 'callback_extension', '?')
    s.check_bogus_field_returns_error(url, 'callback_extension', 'value with space')
    s.check_bogus_field_returns_error(url, 'callback_extension', 123)
    s.check_bogus_field_returns_error(url, 'callback_extension', True)
    s.check_bogus_field_returns_error(url, 'callback_extension', [])
    s.check_bogus_field_returns_error(url, 'callback_extension', {})
    s.check_bogus_field_returns_error(url, 'callback_context', 123)
    s.check_bogus_field_returns_error(url, 'callback_context', True)
    s.check_bogus_field_returns_error(url, 'callback_context', [])
    s.check_bogus_field_returns_error(url, 'callback_context', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'string')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])


@fixtures.register_iax()
def test_get(register_iax):
    response = confd.registers.iax(register_iax['id']).get()
    assert_that(response.item, has_entries(
        id=register_iax['id'],
        auth_username=none(),
        auth_password=none(),
        remote_host=register_iax['remote_host'],
        remote_port=none(),
        callback_extension=none(),
        callback_context=none(),
        enabled=True,
        trunk=none(),
    ))


def test_create_minimal_parameters():
    response = confd.registers.iax.post(remote_host='remote-host')
    response.assert_created('register_iax', location='registers/iax')

    assert_that(response.item, has_entries(
        id=not_(empty()),
        remote_host='remote-host',
    ))


def test_create_all_parameters():
    parameters = dict(
        auth_username='auth-username',
        auth_password='auth-password',
        remote_host='remote-host',
        remote_port=1234,
        callback_extension='callback-extension',
        callback_context='callback-context',
        enabled=True
    )
    response = confd.registers.iax.post(**parameters)

    response.assert_created('register_iax', location='registers/iax')
    assert_that(response.item, has_entries(id=not_(empty()), **parameters))


@fixtures.register_iax()
def test_edit_minimal_parameters(register_iax):
    parameters = {}

    response = confd.registers.iax(register_iax['id']).put(**parameters)
    response.assert_updated()


@fixtures.register_iax()
def test_edit_all_parameters(register_iax):
    parameters = dict(
        auth_username='auth-username',
        auth_password='auth-password',
        remote_host='remote-host',
        remote_port=1234,
        callback_extension='callback-extension',
        callback_context='callback-context',
        enabled=False
    )

    response = confd.registers.iax(register_iax['id']).put(**parameters)
    response.assert_updated()

    response = confd.registers.iax(register_iax['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.register_iax()
def test_delete(register_iax):
    response = confd.registers.iax(register_iax['id']).delete()
    response.assert_deleted()


@fixtures.register_iax()
def test_bus_events(register_iax):
    s.check_bus_event('config.register.iax.created', confd.registers.iax.post, {'remote_host': 'bus-event'})
    s.check_bus_event('config.register.iax.edited', confd.registers.iax(register_iax['id']).put)
    s.check_bus_event('config.register.iax.deleted', confd.registers.iax(register_iax['id']).delete)
