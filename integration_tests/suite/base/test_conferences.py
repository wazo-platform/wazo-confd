# -*- coding: utf-8 -*-

# Copyright (C) 2016 Francois Blackburn
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
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


def test_get_errors():
    fake_conference = confd.conferences(999999).get
    yield s.check_resource_not_found, fake_conference, 'Conference'


def test_delete_errors():
    fake_conference = confd.conferences(999999).delete
    yield s.check_resource_not_found, fake_conference, 'Conference'


def test_post_errors():
    url = confd.conferences.post
    for check in error_checks(url):
        yield check


@fixtures.conference()
def test_put_errors(conference):
    url = confd.conferences(conference['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', True
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 1234
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', True
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', None
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', []
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', {}
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', None
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', []
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', {}
    yield s.check_bogus_field_returns_error, url, 'notify_join_leave', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'notify_join_leave', None
    yield s.check_bogus_field_returns_error, url, 'notify_join_leave', []
    yield s.check_bogus_field_returns_error, url, 'notify_join_leave', {}
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', None
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', []
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', {}
    yield s.check_bogus_field_returns_error, url, 'record', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'record', None
    yield s.check_bogus_field_returns_error, url, 'record', []
    yield s.check_bogus_field_returns_error, url, 'record', {}
    yield s.check_bogus_field_returns_error, url, 'pin', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'pin', None
    yield s.check_bogus_field_returns_error, url, 'pin', []
    yield s.check_bogus_field_returns_error, url, 'pin', {}
    yield s.check_bogus_field_returns_error, url, 'admin_pin', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'admin_pin', None
    yield s.check_bogus_field_returns_error, url, 'admin_pin', []
    yield s.check_bogus_field_returns_error, url, 'admin_pin', {}


@fixtures.conference(name='search', preprocess_subroutine='search')
@fixtures.conference(name='hidden', preprocess_subroutine='hidden')
def test_search(conference, hidden):
    url = confd.conferences
    searches = {'name': 'search',
                'preprocess_subroutine': 'search'}

    for field, term in searches.items():
        yield check_search, url, conference, hidden, field, term


def check_search(url, conference, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, conference[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: conference[field]})

    expected = has_item(has_entry('id', conference['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.conference(name='sort1')
@fixtures.conference(name='sort2')
def test_sorting_offset_limit(conference1, conference2):
    url = confd.conferences.get
    yield s.check_sorting, url, conference1, conference2, 'name', 'sort'

    yield s.check_offset, url, conference1, conference2, 'name', 'sort'
    yield s.check_offset_legacy, url, conference1, conference2, 'name', 'sort'

    yield s.check_limit, url, conference1, conference2, 'name', 'sort'


@fixtures.conference()
def test_get(conference):
    response = confd.conferences(conference['id']).get()
    assert_that(response.item, has_entries(id=conference['id'],
                                           name=conference['name'],
                                           preprocess_subroutine=conference['preprocess_subroutine'],
                                           max_users=conference['max_users'],
                                           record=conference['record'],
                                           pin=conference['pin'],
                                           admin_pin=conference['admin_pin'],
                                           notify_join_leave=conference['notify_join_leave'],
                                           announce_join_leave=conference['announce_join_leave'],
                                           announce_user_count=conference['announce_user_count'],
                                           announce_only_user=conference['announce_only_user'],
                                           music_on_hold=conference['music_on_hold'],
                                           extensions=empty()))


def test_create_minimal_parameters():
    response = confd.conferences.post(name='MyConference')
    response.assert_created('conferences')

    assert_that(response.item, has_entries(id=not_(empty())))

    confd.conferences(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyConference',
                  'preprocess_subroutine': 'subroutine',
                  'max_users': 150,
                  'record': True,
                  'pin': '7654',
                  'admin_pin': '7654',
                  'notify_join_leave': False,
                  'announce_join_leave': True,
                  'announce_user_count': True,
                  'announce_only_user': False,
                  'music_on_hold': 'music'}

    response = confd.conferences.post(**parameters)
    response.assert_created('conferences')
    response = confd.conferences(response.item['id']).get()

    assert_that(response.item, has_entries(parameters))

    confd.conferences(response.item['id']).delete().assert_deleted()


@fixtures.conference()
def test_edit_minimal_parameters(conference):
    response = confd.conferences(conference['id']).put()
    response.assert_updated()


@fixtures.conference()
def test_edit_all_parameters(conference):
    parameters = {'name': 'MyConference',
                  'preprocess_subroutine': 'subroutine',
                  'max_users': 150,
                  'record': True,
                  'pin': '7654',
                  'admin_pin': '7654',
                  'notify_join_leave': False,
                  'announce_join_leave': True,
                  'announce_user_count': True,
                  'announce_only_user': False,
                  'music_on_hold': 'music'}

    response = confd.conferences(conference['id']).put(**parameters)
    response.assert_updated()

    response = confd.conferences(conference['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.conference()
def test_delete(conference):
    response = confd.conferences(conference['id']).delete()
    response.assert_deleted()
    response = confd.conferences(conference['id']).get()
    response.assert_match(404, e.not_found(resource='Conference'))


@fixtures.conference()
def test_bus_events(conference):
    yield s.check_bus_event, 'config.conferences.created', confd.conferences.post
    yield s.check_bus_event, 'config.conferences.edited', confd.conferences(conference['id']).put
    yield s.check_bus_event, 'config.conferences.deleted', confd.conferences(conference['id']).delete
