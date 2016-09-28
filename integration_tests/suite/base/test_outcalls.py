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

from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s
from test_api.config import CONTEXT

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


def test_get_errors():
    fake_outcall = confd.outcalls(999999).get
    yield s.check_resource_not_found, fake_outcall, 'Outcall'


def test_delete_errors():
    fake_outcall = confd.outcalls(999999).delete
    yield s.check_resource_not_found, fake_outcall, 'Outcall'


def test_post_errors():
    url = confd.outcalls.post
    for check in error_checks(url):
        yield check


@fixtures.outcall()
def test_put_errors(outcall):
    url = confd.outcalls(outcall['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', 1234
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', None
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', []
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'ring_time', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'ring_time', []
    yield s.check_bogus_field_returns_error, url, 'ring_time', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}

    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'prefix': True}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'prefix': s.random_digits(33)}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'prefix': 'invalid_regex'}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'external_prefix': True}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'external_prefix': s.random_digits(65)}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'external_prefix': 'invalid_regex'}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'caller_id': True}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'caller_id': s.random_string(81)}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'strip_digits': 'invalid'}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'X', 'strip_digits': -1}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': True}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': None}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': s.random_digits(41)}
    yield s.check_bogus_field_returns_error, url, 'patterns', {'pattern': 'invalid_regex'}

    for check in unique_error_checks(url):
        yield check


@fixtures.outcall(name='unique')
def unique_error_checks(url, outcall):
    required_field = {'context': CONTEXT}
    yield s.check_bogus_field_returns_error, url, 'name', outcall['name'], required_field


@fixtures.outcall(description='search')
@fixtures.outcall(description='hidden')
def test_search(outcall, hidden):
    url = confd.outcalls
    searches = {'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, outcall, hidden, field, term


def check_search(url, outcall, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, outcall[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: outcall[field]})

    expected = has_item(has_entry('id', outcall['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.outcall(description='sort1')
@fixtures.outcall(description='sort2')
def test_sorting(outcall1, outcall2):
    yield check_sorting, outcall1, outcall2, 'description', 'sort'


def check_sorting(outcall1, outcall2, field, search):
    response = confd.outcalls.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=outcall1['id']),
                                         has_entries(id=outcall2['id'])))

    response = confd.outcalls.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=outcall2['id']),
                                         has_entries(id=outcall1['id'])))


@fixtures.outcall()
def test_get(outcall):
    response = confd.outcalls(outcall['id']).get()
    assert_that(response.item, has_entries(id=outcall['id'],
                                           preprocess_subroutine=outcall['preprocess_subroutine'],
                                           description=outcall['description'],
                                           internal_caller_id=outcall['internal_caller_id'],
                                           name=outcall['name'],
                                           context=outcall['context'],
                                           ring_time=outcall['ring_time'],
                                           patterns=outcall['patterns']))


def test_create_minimal_parameters():
    response = confd.outcalls.post(name='MyOutcall', context=CONTEXT)
    response.assert_created('outcalls')

    assert_that(response.item, has_entries(id=not_(empty())))

    confd.outcalls(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyOutcall',
                  'context': CONTEXT,
                  'internal_caller_id': True,
                  'preprocess_subroutine': 'subroutine',
                  'ring_time': 10,
                  'description': 'outcall description',
                  'patterns': [{'pattern': '**.',
                                'prefix': '9',
                                'external_prefix': '1',
                                'strip_digits': 2,
                                'caller_id': 'OUT'}]}

    response = confd.outcalls.post(**parameters)
    response.assert_created('outcalls')

    assert_that(response.item, has_entries(parameters))

    confd.outcalls(response.item['id']).delete().assert_deleted()


@fixtures.outcall()
def test_edit_minimal_parameters(outcall):
    response = confd.outcalls(outcall['id']).put()
    response.assert_updated()


@fixtures.outcall()
def test_edit_all_parameters(outcall):
    parameters = {'name': 'MyOutcall',
                  'context': CONTEXT,
                  'internal_caller_id': True,
                  'preprocess_subroutine': 'subroutine',
                  'ring_time': 10,
                  'description': 'outcall description',
                  'patterns': [{'pattern': '**.',
                                'prefix': '9',
                                'external_prefix': '1',
                                'strip_digits': 2,
                                'caller_id': 'OUT'}]}

    response = confd.outcalls(outcall['id']).put(**parameters)
    response.assert_updated()

    response = confd.outcalls(outcall['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.outcall()
def test_delete(outcall):
    response = confd.outcalls(outcall['id']).delete()
    response.assert_deleted()
    response = confd.outcalls(outcall['id']).get()
    response.assert_match(404, e.not_found(resource='Outcall'))


@fixtures.outcall()
def test_bus_events(outcall):
    yield s.check_bus_event, 'config.outcalls.created', confd.outcalls.post, {'name': 'a',
                                                                              'context': CONTEXT}
    yield s.check_bus_event, 'config.outcalls.updated', confd.outcalls(outcall['id']).put
    yield s.check_bus_event, 'config.outcalls.deleted', confd.outcalls(outcall['id']).delete
