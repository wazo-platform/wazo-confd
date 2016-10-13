# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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


from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e

from hamcrest import assert_that, has_entries, has_items, instance_of, has_entry


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
    long_interface = "a" * 129
    yield s.check_bogus_field_returns_error, url, 'interface', None
    yield s.check_bogus_field_returns_error, url, 'interface', 'custom/&&&~~~'
    yield s.check_bogus_field_returns_error, url, 'interface', long_interface
    yield s.check_bogus_field_returns_error, url, 'interface', []
    yield s.check_bogus_field_returns_error, url, 'interface', {}


@fixtures.custom()
def test_delete_errors(custom):
    url = confd.endpoints.custom(custom['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'CustomEndpoint'


@fixtures.custom()
def test_get(custom):
    expected = has_entries({'id': instance_of(int),
                            'interface': custom['interface'],
                            'enabled': True,
                            'trunk': None})

    response = confd.endpoints.custom(custom['id']).get()
    assert_that(response.item, expected)


@fixtures.custom()
@fixtures.custom()
def test_list(custom1, custom2):
    expected = has_items(has_entry('id', custom1['id']),
                         has_entry('id', custom2['id']))

    response = confd.endpoints.custom.get()
    assert_that(response.items, expected)


def test_create_custom_minimal_parameters():
    expected = has_entries({'id': instance_of(int),
                            'interface': 'custom/createmin',
                            'enabled': True})

    response = confd.endpoints.custom.post(interface='custom/createmin')

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, expected)


def test_create_custom_all_parameters():
    expected = has_entries({'id': instance_of(int),
                            'interface': 'custom/createall',
                            'enabled': False})

    response = confd.endpoints.custom.post(interface='custom/createall',
                                           enabled=False)

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, expected)


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
    url = confd.endpoints.custom(custom['id'])
    response = url.put(interface='custom/afterupdate',
                       enabled=False)
    response.assert_updated()

    response = url.get()
    assert_that(response.item, has_entries(interface='custom/afterupdate',
                                           enabled=False))


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
