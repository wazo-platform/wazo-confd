# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
    fake_register_iax = confd.registers.iax(999999).get
    yield s.check_resource_not_found, fake_register_iax, 'IAXRegister'


def test_delete_errors():
    fake_register_iax = confd.registers.iax(999999).delete
    yield s.check_resource_not_found, fake_register_iax, 'IAXRegister'


def test_post_errors():
    url = confd.registers.iax.post
    for check in error_checks(url):
        yield check


@fixtures.register_iax()
def test_put_errors(register_iax):
    url = confd.registers.iax(register_iax['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'auth_password', ':'
    yield s.check_bogus_field_returns_error, url, 'auth_password', '/'
    yield s.check_bogus_field_returns_error, url, 'auth_password', 'value with space'
    yield s.check_bogus_field_returns_error, url, 'auth_password', 123
    yield s.check_bogus_field_returns_error, url, 'auth_password', True
    yield s.check_bogus_field_returns_error, url, 'auth_password', []
    yield s.check_bogus_field_returns_error, url, 'auth_password', {}
    yield s.check_bogus_field_returns_error, url, 'auth_username', ':'
    yield s.check_bogus_field_returns_error, url, 'auth_username', '/'
    yield s.check_bogus_field_returns_error, url, 'auth_username', 'value with space'
    yield s.check_bogus_field_returns_error, url, 'auth_username', 123
    yield s.check_bogus_field_returns_error, url, 'auth_username', True
    yield s.check_bogus_field_returns_error, url, 'auth_username', []
    yield s.check_bogus_field_returns_error, url, 'auth_username', {}
    yield s.check_bogus_field_returns_error, url, 'remote_host', ':'
    yield s.check_bogus_field_returns_error, url, 'remote_host', '/'
    yield s.check_bogus_field_returns_error, url, 'remote_host', '?'
    yield s.check_bogus_field_returns_error, url, 'remote_host', 'value with space'
    yield s.check_bogus_field_returns_error, url, 'remote_host', 123
    yield s.check_bogus_field_returns_error, url, 'remote_host', True
    yield s.check_bogus_field_returns_error, url, 'remote_host', []
    yield s.check_bogus_field_returns_error, url, 'remote_host', {}
    yield s.check_bogus_field_returns_error, url, 'remote_port', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'remote_port', []
    yield s.check_bogus_field_returns_error, url, 'remote_port', {}
    yield s.check_bogus_field_returns_error, url, 'callback_extension', '?'
    yield s.check_bogus_field_returns_error, url, 'callback_extension', 'value with space'
    yield s.check_bogus_field_returns_error, url, 'callback_extension', 123
    yield s.check_bogus_field_returns_error, url, 'callback_extension', True
    yield s.check_bogus_field_returns_error, url, 'callback_extension', []
    yield s.check_bogus_field_returns_error, url, 'callback_extension', {}
    yield s.check_bogus_field_returns_error, url, 'callback_context', 123
    yield s.check_bogus_field_returns_error, url, 'callback_context', True
    yield s.check_bogus_field_returns_error, url, 'callback_context', []
    yield s.check_bogus_field_returns_error, url, 'callback_context', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'string'
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []


@fixtures.register_iax()
def test_get(register_iax):
    response = confd.registers.iax(register_iax['id']).get()
    assert_that(response.item, has_entries(
        id=register_iax['id'],
        auth_password=none(),
        auth_username=none(),
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
        auth_password='auth-password',
        auth_username='auth-username',
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
        auth_password='auth-password',
        auth_username='auth-username',
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
    yield s.check_bus_event, 'config.register.iax.created', confd.registers.iax.post, {'remote_host': 'bus-event'}
    yield s.check_bus_event, 'config.register.iax.edited', confd.registers.iax(register_iax['id']).put
    yield s.check_bus_event, 'config.register.iax.deleted', confd.registers.iax(register_iax['id']).delete
