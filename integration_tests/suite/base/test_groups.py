# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


def test_get_errors():
    fake_group = confd.groups(999999).get
    yield s.check_resource_not_found, fake_group, 'Group'


def test_delete_errors():
    fake_group = confd.groups(999999).delete
    yield s.check_resource_not_found, fake_group, 'Group'


def test_post_errors():
    url = confd.groups.post
    for check in error_checks(url):
        yield check


@fixtures.group()
def test_put_errors(group):
    url = confd.groups(group['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', 123
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', True
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', None
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', []
    yield s.check_bogus_field_returns_error, url, 'ring_strategy', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'user_timeout', 'ten'
    yield s.check_bogus_field_returns_error, url, 'user_timeout', -1
    yield s.check_bogus_field_returns_error, url, 'user_timeout', {}
    yield s.check_bogus_field_returns_error, url, 'user_timeout', []
    yield s.check_bogus_field_returns_error, url, 'retry_delay', 'ten'
    yield s.check_bogus_field_returns_error, url, 'retry_delay', -1
    yield s.check_bogus_field_returns_error, url, 'retry_delay', {}
    yield s.check_bogus_field_returns_error, url, 'retry_delay', []
    yield s.check_bogus_field_returns_error, url, 'timeout', 'ten'
    yield s.check_bogus_field_returns_error, url, 'timeout', -1
    yield s.check_bogus_field_returns_error, url, 'timeout', {}
    yield s.check_bogus_field_returns_error, url, 'timeout', []
    yield s.check_bogus_field_returns_error, url, 'ring_in_use', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'ring_in_use', 123
    yield s.check_bogus_field_returns_error, url, 'ring_in_use', {}
    yield s.check_bogus_field_returns_error, url, 'ring_in_use', []
    yield s.check_bogus_field_returns_error, url, 'enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []

    for check in unique_error_checks(url):
        yield check


@fixtures.group(name='unique')
def unique_error_checks(url, group):
    yield s.check_bogus_field_returns_error, url, 'name', group['name']


@fixtures.group(name='hidden', preprocess_subroutine='hidden')
@fixtures.group(name='search', preprocess_subroutine='search')
def test_search(hidden, group):
    url = confd.groups
    searches = {'name': 'search',
                'preprocess_subroutine': 'search'}

    for field, term in searches.items():
        yield check_search, url, group, hidden, field, term


def check_search(url, group, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, group[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: group[field]})

    expected = has_item(has_entry('id', group['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.group(name='sort1', preprocess_subroutine='sort1')
@fixtures.group(name='sort2', preprocess_subroutine='sort2')
def test_sorting(group1, group2):
    yield check_sorting, group1, group2, 'name', 'sort'
    yield check_sorting, group1, group2, 'preprocess_subroutine', 'sort'


def check_sorting(group1, group2, field, search):
    response = confd.groups.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=group1['id']),
                                         has_entries(id=group2['id'])))

    response = confd.groups.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=group2['id']),
                                         has_entries(id=group1['id'])))


@fixtures.group()
def test_get(group):
    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(id=group['id'],
                                           name=group['name'],
                                           caller_id_mode=group['caller_id_mode'],
                                           caller_id_name=group['caller_id_name'],
                                           timeout=group['timeout'],
                                           music_on_hold=group['music_on_hold'],
                                           preprocess_subroutine=group['preprocess_subroutine'],
                                           ring_in_use=group['ring_in_use'],
                                           ring_strategy=group['ring_strategy'],
                                           user_timeout=group['user_timeout'],
                                           retry_delay=group['retry_delay'],
                                           enabled=group['enabled']))


def test_create_minimal_parameters():
    response = confd.groups.post(name='MyGroup')
    response.assert_created('groups')

    assert_that(response.item, has_entries(id=not_(empty()),
                                           name='MyGroup'))

    confd.groups(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyGroup',
                  'caller_id_mode': 'prepend',
                  'caller_id_name': 'GROUP-',
                  'timeout': 42,
                  'music_on_hold': 'default',
                  'preprocess_subroutine': 'subroutien',
                  'ring_in_use': False,
                  'ring_strategy': 'weight_random',
                  'user_timeout': 24,
                  'retry_delay': 12,
                  'enabled': False}

    response = confd.groups.post(**parameters)
    response.assert_created('groups')

    assert_that(response.item, has_entries(parameters))

    confd.groups(response.item['id']).delete().assert_deleted()


@fixtures.group()
def test_edit_minimal_parameters(group):
    response = confd.groups(group['id']).put()
    response.assert_updated()


@fixtures.group()
def test_edit_all_parameters(group):
    parameters = {'name': 'MyGroup',
                  'caller_id_mode': 'prepend',
                  'caller_id_name': 'GROUP-',
                  'timeout': 42,
                  'music_on_hold': 'default',
                  'preprocess_subroutine': 'subroutien',
                  'ring_in_use': False,
                  'ring_strategy': 'random',
                  'user_timeout': 24,
                  'retry_delay': 12,
                  'enabled': False}

    response = confd.groups(group['id']).put(**parameters)
    response.assert_updated()

    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.group()
def test_delete(group):
    response = confd.groups(group['id']).delete()
    response.assert_deleted()
    response = confd.groups(group['id']).get()
    response.assert_match(404, e.not_found(resource='Group'))


@fixtures.group()
def test_bus_events(group):
    yield s.check_bus_event, 'config.groups.created', confd.groups.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.groups.edited', confd.groups(group['id']).put
    yield s.check_bus_event, 'config.groups.deleted', confd.groups(group['id']).delete
