# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from test_api import scenarios as s
from test_api import errors as e
from test_api import fixtures
from test_api import confd

from hamcrest import (assert_that,
                      contains,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not)


def test_get_errors():
    fake_get = confd.permissions(999999).get
    yield s.check_resource_not_found, fake_get, 'Permission'


def test_post_errors():
    url = confd.permissions.post
    for check in error_checks(url):
        yield check


@fixtures.permission()
def test_put_errors(permission):
    url = confd.permissions(permission['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', True
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', True
    yield s.check_bogus_field_returns_error, url, 'mode', 123
    yield s.check_bogus_field_returns_error, url, 'mode', None
    yield s.check_bogus_field_returns_error, url, 'mode', False
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'extensions', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'extensions', 123
    yield s.check_bogus_field_returns_error, url, 'extensions', True
    yield s.check_bogus_field_returns_error, url, 'extensions', None


@fixtures.permission(name="search",
                     password="123",
                     description="SearchDesc",
                     mode='deny',
                     enabled=True)
@fixtures.permission(name="hidden",
                     password="456",
                     description="HiddenDesc",
                     mode='allow',
                     enabled=False)
def test_search_on_permission(permission, hidden):
    url = confd.permissions
    searches = {'name': 'search',
                'description': 'Search',
                'mode': 'deny',
                'enabled': True}

    for field, term in searches.items():
        yield check_search, url, permission, hidden, field, term


@fixtures.permission(name="sort1",
                     description="Sort 1")
@fixtures.permission(name="sort2",
                     description="Sort 2")
def test_permission_sorting(permission1, permission2):
    yield check_permission_sorting, permission1, permission2, 'name', 'sort'
    yield check_permission_sorting, permission1, permission2, 'description', 'Sort'


def check_permission_sorting(permission1, permission2, field, search):
    response = confd.permissions.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=permission1['id']),
                                         has_entries(id=permission2['id'])))

    response = confd.permissions.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=permission2['id']),
                                         has_entries(id=permission1['id'])))


def check_search(url, permission, hidden, field, term):
    response = url.get(search=term)

    expected_permission = has_item(has_entry(field, permission[field]))
    hidden_permission = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_permission)
    assert_that(response.items, hidden_permission)

    response = url.get(**{field: permission[field]})

    expected_permission = has_item(has_entry('id', permission['id']))
    hidden_permission = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_permission)
    assert_that(response.items, hidden_permission)


@fixtures.permission(name="search",
                     password="123",
                     description="SearchDesc",
                     mode='deny',
                     enabled=True,
                     extensions=['123', '456'])
def test_get(permission):
    response = confd.permissions(permission['id']).get()
    assert_that(response.item, has_entries(name='search',
                                           password='123',
                                           description='SearchDesc',
                                           mode='deny',
                                           enabled=True,
                                           extensions=['123', '456']))


def test_create_permission_minimal_parameters():
    response = confd.permissions.post(name='minimal')
    response.assert_created('permissions')

    assert_that(response.item, has_entries(name='minimal',
                                           password=None,
                                           description=None,
                                           mode='deny',
                                           enabled=True,
                                           extensions=[]))


def test_create_permission_all_parameters():
    parameters = {'name': 'allparameter',
                  'password': '1234',
                  'description': 'Create description',
                  'mode': 'allow',
                  'enabled': False,
                  'extensions': ['123', '*456', '963']}

    response = confd.permissions.post(**parameters)
    response.assert_created('permissions')
    assert_that(response.item, has_entries(parameters))


@fixtures.permission()
def test_create_2_permissions_with_same_name(permission):
    response = confd.permissions.post(name=permission['name'])
    response.assert_match(400, e.resource_exists('Permission'))


@fixtures.permission()
def test_create_permissions_with_invalid_mode(permission):
    response = confd.permissions.post(name=permission['name'], mode='invalidmode')
    response.assert_status(400)


def test_create_permissions_with_duplicate_extensions():
    parameters = {'name': 'duplicate_perm',
                  'extensions': ['123', '123', '456']}

    response = confd.permissions.post(**parameters)
    response.assert_created('permissions')
    assert_that(response.item, has_entries(name=parameters['name'],
                                           extensions=['123', '456']))


@fixtures.permission(name='name1', extension=['123'])
def test_edit_permission_all_parameters(permission):
    parameters = {'name': 'second',
                  'password': '1234',
                  'description': 'Create description',
                  'mode': 'allow',
                  'enabled': False,
                  'extensions': ['123', '*456', '963']}

    response = confd.permissions(permission['id']).put(**parameters)
    response.assert_updated()

    response = confd.permissions(permission['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.permission(name='permission1')
@fixtures.permission(name='permission2')
def test_edit_permission_with_same_name(first_permission, second_permission):
    response = confd.permissions(first_permission['id']).put(name=second_permission['name'])
    response.assert_match(400, e.resource_exists('Permission'))


@fixtures.permission()
def test_delete_permission(permission):
    response = confd.permissions(permission['id']).delete()
    response.assert_deleted()
