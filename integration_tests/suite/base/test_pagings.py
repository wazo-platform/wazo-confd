# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)
from . import confd


def test_get_errors():
    fake_paging = confd.pagings(999999).get
    yield s.check_resource_not_found, fake_paging, 'Paging'


def test_delete_errors():
    fake_paging = confd.pagings(999999).delete
    yield s.check_resource_not_found, fake_paging, 'Paging'


def test_post_errors():
    url = confd.pagings.post
    for check in error_checks(url):
        yield check


@fixtures.paging()
def test_put_errors(paging):
    url = confd.pagings(paging['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'number', True
    yield s.check_bogus_field_returns_error, url, 'number', 123
    yield s.check_bogus_field_returns_error, url, 'number', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'number', []
    yield s.check_bogus_field_returns_error, url, 'number', {}
    yield s.check_bogus_field_returns_error, url, 'announce_caller', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_caller', None
    yield s.check_bogus_field_returns_error, url, 'announce_caller', []
    yield s.check_bogus_field_returns_error, url, 'announce_caller', {}
    yield s.check_bogus_field_returns_error, url, 'announce_sound', True
    yield s.check_bogus_field_returns_error, url, 'announce_sound', 1234
    yield s.check_bogus_field_returns_error, url, 'announce_sound', []
    yield s.check_bogus_field_returns_error, url, 'announce_sound', {}
    yield s.check_bogus_field_returns_error, url, 'duplex', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'duplex', None
    yield s.check_bogus_field_returns_error, url, 'duplex', []
    yield s.check_bogus_field_returns_error, url, 'duplex', {}
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', None
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', []
    yield s.check_bogus_field_returns_error, url, 'ignore_forward', {}
    yield s.check_bogus_field_returns_error, url, 'record', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'record', None
    yield s.check_bogus_field_returns_error, url, 'record', []
    yield s.check_bogus_field_returns_error, url, 'record', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.paging(number='123')
def unique_error_checks(url, paging):
    yield s.check_bogus_field_returns_error, url, 'number', paging['number']


@fixtures.paging(name='search', number='123', announce_sound='search')
@fixtures.paging(name='hidden', number='456', announce_sound='hidden')
def test_search(paging, hidden):
    url = confd.pagings
    searches = {'name': 'search',
                'number': '123',
                'announce_sound': 'search'}

    for field, term in searches.items():
        yield check_search, url, paging, hidden, field, term


def check_search(url, paging, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, paging[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: paging[field]})

    expected = has_item(has_entry('id', paging['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.paging(name='sort1')
@fixtures.paging(name='sort2')
def test_sort_offset_limit(paging1, paging2):
    url = confd.pagings.get
    yield s.check_sorting, url, paging1, paging2, 'name', 'sort'

    yield s.check_offset, url, paging1, paging2, 'name', 'sort'
    yield s.check_offset_legacy, url, paging1, paging2, 'name', 'sort'

    yield s.check_limit, url, paging1, paging2, 'name', 'sort'


@fixtures.paging()
def test_get(paging):
    response = confd.pagings(paging['id']).get()
    assert_that(response.item, has_entries(id=paging['id'],
                                           name=paging['name'],
                                           number=paging['number'],
                                           announce_caller=paging['announce_caller'],
                                           announce_sound=paging['announce_sound'],
                                           caller_notification=paging['caller_notification'],
                                           duplex=paging['duplex'],
                                           ignore_forward=paging['ignore_forward'],
                                           record=paging['record'],
                                           enabled=paging['enabled']))


def test_create_minimal_parameters():
    response = confd.pagings.post(number='123')
    response.assert_created('pagings')

    assert_that(response.item, has_entries(id=not_(empty())))

    confd.pagings(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyPaging',
                  'number': '123',
                  'announce_caller': False,
                  'announce_sound': 'sound',
                  'caller_notification': True,
                  'duplex': True,
                  'ignore_forward': True,
                  'record': True,
                  'enabled': False}

    response = confd.pagings.post(**parameters)
    response.assert_created('pagings')
    response = confd.pagings(response.item['id']).get()

    assert_that(response.item, has_entries(parameters))

    confd.pagings(response.item['id']).delete().assert_deleted()


@fixtures.paging()
def test_edit_minimal_parameters(paging):
    response = confd.pagings(paging['id']).put()
    response.assert_updated()


@fixtures.paging()
def test_edit_all_parameters(paging):
    parameters = {'name': 'MyPaging',
                  'number': '123',
                  'announce_caller': False,
                  'announce_sound': 'sound',
                  'caller_notification': True,
                  'duplex': True,
                  'ignore_forward': True,
                  'record': True,
                  'enabled': False}

    response = confd.pagings(paging['id']).put(**parameters)
    response.assert_updated()

    response = confd.pagings(paging['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.paging()
def test_delete(paging):
    response = confd.pagings(paging['id']).delete()
    response.assert_deleted()
    response = confd.pagings(paging['id']).get()
    response.assert_match(404, e.not_found(resource='Paging'))


@fixtures.paging()
def test_bus_events(paging):
    yield s.check_bus_event, 'config.pagings.created', confd.pagings.post, {'number': '666'}
    yield s.check_bus_event, 'config.pagings.edited', confd.pagings(paging['id']).put
    yield s.check_bus_event, 'config.pagings.deleted', confd.pagings(paging['id']).delete
