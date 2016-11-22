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
                      has_item,
                      has_entry,
                      is_not,
                      not_)

NOT_FOUND_SWITCHBOARD_ID = 999999


def test_get_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_ID).get
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_delete_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_ID).delete
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_post_errors():
    url = confd.switchboards.post
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}


@fixtures.switchboard(name='hidden', preprocess_subroutine='hidden')
@fixtures.switchboard(name='search', preprocess_subroutine='search')
def test_search(hidden, switchboard):
    url = confd.switchboards
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, switchboard, hidden, field, term


def check_search(url, switchboard, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, switchboard[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: switchboard[field]})

    expected = has_item(has_entry('id', switchboard['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.switchboard(name='sort1')
@fixtures.switchboard(name='sort2')
def test_sorting(switchboard1, switchboard2):
    yield check_sorting, switchboard1, switchboard2, 'name', 'sort'


def check_sorting(switchboard1, switchboard2, field, search):
    response = confd.switchboards.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=switchboard1['id']),
                                         has_entries(id=switchboard2['id'])))

    response = confd.switchboards.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=switchboard2['id']),
                                         has_entries(id=switchboard1['id'])))


@fixtures.switchboard()
def test_get(switchboard):
    response = confd.switchboards(switchboard['id']).get()
    assert_that(response.item, has_entries(id=switchboard['id'],
                                           name=switchboard['name']))


def test_create_minimal_parameters():
    response = confd.switchboards.post(name='MySwitchboard')
    response.assert_created('switchboards')

    assert_that(response.item, has_entries(id=not_(empty()),
                                           name='MySwitchboard'))

    confd.switchboards(response.item['id']).delete().assert_deleted()


@fixtures.switchboard()
def test_delete(switchboard):
    response = confd.switchboards(switchboard['id']).delete()
    response.assert_deleted()
    response = confd.switchboards(switchboard['id']).get()
    response.assert_match(404, e.not_found(resource='Switchboard'))


@fixtures.switchboard()
def test_bus_events(switchboard):
    yield s.check_bus_event, 'config.switchboards.*.created', confd.switchboards.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.switchboards.{id}.deleted'.format(id=switchboard['id']), confd.switchboards(switchboard['id']).delete
