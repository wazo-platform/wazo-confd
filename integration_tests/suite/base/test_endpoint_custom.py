# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_items,
    instance_of,
)

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers import errors as e
from . import confd


def test_get_errors():
    fake_custom_get = confd.endpoints.custom(999999).get
    yield s.check_resource_not_found, fake_custom_get, 'CustomEndpoint'


def test_post_errors():
    url = confd.endpoints.custom.post
    for check in error_checks(url):
        yield check


@fixtures.custom()
def test_put_errors(custom):
    url = confd.endpoints.custom(custom['id']).put

    yield s.check_bogus_field_returns_error, url, 'enabled', None

    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'interface', None
    yield s.check_bogus_field_returns_error, url, 'interface', True
    yield s.check_bogus_field_returns_error, url, 'interface', 'custom/&&&~~~'
    yield s.check_bogus_field_returns_error, url, 'interface', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'interface', []
    yield s.check_bogus_field_returns_error, url, 'interface', {}
    yield s.check_bogus_field_returns_error, url, 'interface_suffix', True
    yield s.check_bogus_field_returns_error, url, 'interface_suffix', s.random_string(33)
    yield s.check_bogus_field_returns_error, url, 'interface_suffix', []
    yield s.check_bogus_field_returns_error, url, 'interface_suffix', {}


@fixtures.custom()
def test_delete_errors(custom):
    url = confd.endpoints.custom(custom['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'CustomEndpoint'


@fixtures.custom()
def test_get(custom):
    response = confd.endpoints.custom(custom['id']).get()
    assert_that(response.item, has_entries({
        'id': instance_of(int),
        'interface': custom['interface'],
        'interface_suffix': custom['interface_suffix'],
        'enabled': True,
        'trunk': None,
        'line': None,
    }))


@fixtures.custom()
@fixtures.custom()
def test_list(custom1, custom2):
    response = confd.endpoints.custom.get()
    assert_that(response.items, has_items(
        has_entry('id', custom1['id']),
        has_entry('id', custom2['id']),
    ))


def test_create_custom_minimal_parameters():
    response = confd.endpoints.custom.post(interface='custom/createmin')

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, has_entries({
        'id': instance_of(int),
        'interface': 'custom/createmin',
        'enabled': True,
    }))


def test_create_custom_all_parameters():
    response = confd.endpoints.custom.post(interface='custom/createall',
                                           enabled=False)

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, has_entries({
        'id': instance_of(int),
        'interface': 'custom/createall',
        'enabled': False
    }))


def test_create_custom_accept_uppercase_interface():
    response = confd.endpoints.custom.post(interface='Local/123@foobar')

    response.assert_ok()


def test_given_interface_already_exists_then_error_raised():
    response = confd.endpoints.custom.post(interface='custom/duplicate')
    response.assert_ok()

    response = confd.endpoints.custom.post(interface='custom/duplicate')
    response.assert_match(400, e.resource_exists('CustomEndpoint'))


@fixtures.custom(interface='custom/beforeupdate')
def test_update_custom(custom):
    parameters = {
        'interface': 'custom/afterupdate',
        'interface_suffix': 'other',
        'enabled': False,
    }
    response = confd.endpoints.custom(custom['id']).put(**parameters)
    response.assert_updated()

    response = confd.endpoints.custom(custom['id']).get()
    assert_that(response.item, has_entries(**parameters))


@fixtures.custom()
@fixtures.custom(interface='custom/updateduplicate')
def test_when_updating_custom_with_interface_that_already_exists_then_error_raised(custom, duplicate):
    response = confd.endpoints.custom(custom['id']).put(interface=duplicate['interface'])
    response.assert_match(400, e.resource_exists('CustomEndpoint'))


@fixtures.custom(enabled=False)
def test_when_updating_endpoint_then_values_are_not_overwriten_with_defaults(custom):
    url = confd.endpoints.custom(custom['id'])

    response = url.put(interface="noupdateoverwrite")
    response.assert_ok()

    custom = url.get().item
    assert_that(custom, has_entries(enabled=False))


@fixtures.custom()
def test_delete_custom(custom):
    response = confd.endpoints.custom(custom['id']).delete()
    response.assert_deleted()
