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
    fake_context = confd.contexts(999999).get
    yield s.check_resource_not_found, fake_context, 'Context'


def test_delete_errors():
    fake_context = confd.contexts(999999).delete
    yield s.check_resource_not_found, fake_context, 'Context'


def test_post_errors():
    url = confd.contexts.post
    for check in error_checks(url):
        yield check

    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.context()
def test_put_errors(context):
    url = confd.contexts(context['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'label', 123
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'type', 123
    yield s.check_bogus_field_returns_error, url, 'type', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'type', True
    yield s.check_bogus_field_returns_error, url, 'type', None
    yield s.check_bogus_field_returns_error, url, 'type', []
    yield s.check_bogus_field_returns_error, url, 'type', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'user_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'user_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'user_ranges', True
    yield s.check_bogus_field_returns_error, url, 'user_ranges', None
    yield s.check_bogus_field_returns_error, url, 'user_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'user_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'user_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'group_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'group_ranges', True
    yield s.check_bogus_field_returns_error, url, 'group_ranges', None
    yield s.check_bogus_field_returns_error, url, 'group_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'group_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'group_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', True
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', None
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'queue_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', True
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', None
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'conference_room_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', 123
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', True
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', None
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', {}
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', ['1234']
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'end': '1234'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': None}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': 'invalid'}]
    yield s.check_bogus_field_returns_error, url, 'incall_ranges', [{'start': '123', 'did_length': None}]


@fixtures.context(name='unique')
def unique_error_checks(url, context):
    yield s.check_bogus_field_returns_error, url, 'name', context['name']


@fixtures.context(name='search', type='internal', description='desc_search')
@fixtures.context(name='hidden', type='incall', description='hidden')
def test_search(context, hidden):
    url = confd.contexts
    searches = {'name': 'search',
                'type': 'internal',
                'description': 'desc_search'}

    for field, term in searches.items():
        yield check_search, url, context, hidden, field, term


def check_search(url, context, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, context[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: context[field]})

    expected = has_item(has_entry('id', context['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.context(name='sort1', description='sort1')
@fixtures.context(name='sort2', description='sort2')
def test_sorting(context1, context2):
    yield check_sorting, context1, context2, 'name', 'sort'
    yield check_sorting, context1, context2, 'description', 'sort'


def check_sorting(context1, context2, field, search):
    response = confd.contexts.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=context1['id']),
                                         has_entries(id=context2['id'])))

    response = confd.contexts.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=context2['id']),
                                         has_entries(id=context1['id'])))


@fixtures.context()
def test_get(context):
    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(id=context['id'],
                                           name=context['name'],
                                           label=context['label'],
                                           type=context['type'],
                                           user_ranges=context['user_ranges'],
                                           group_ranges=context['group_ranges'],
                                           queue_ranges=context['queue_ranges'],
                                           conference_room_ranges=context['conference_room_ranges'],
                                           incall_ranges=context['incall_ranges'],
                                           description=context['description'],
                                           enabled=context['enabled']))


def test_create_minimal_parameters():
    response = confd.contexts.post(name='MyContext')
    response.assert_created('contexts')

    assert_that(response.item, has_entries(id=not_(empty())))

    confd.contexts(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyContext',
                  'label': 'Context Power',
                  'type': 'outcall',
                  'user_ranges': [{'start': '1000', 'end': '1999'}],
                  'group_ranges': [{'start': '2000', 'end': '2999'}],
                  'queue_ranges': [{'start': '3000', 'end': '3999'}],
                  'conference_room_ranges': [{'start': '4000', 'end': '4999'}],
                  'incall_ranges': [{'start': '1000', 'end': '4999', 'did_length': 2}],
                  'description': 'context description',
                  'enabled': False}

    response = confd.contexts.post(**parameters)
    response.assert_created('contexts')
    print response

    assert_that(response.item, has_entries(parameters))

    confd.contexts(response.item['id']).delete().assert_deleted()


@fixtures.context()
def test_edit_minimal_parameters(context):
    response = confd.contexts(context['id']).put()
    response.assert_updated()


@fixtures.context()
def test_edit_all_parameters(context):
    parameters = {'label': 'Context Power',
                  'type': 'outcall',
                  'user_ranges': [{'start': '1000', 'end': '1999'}],
                  'group_ranges': [{'start': '2000', 'end': '2999'}],
                  'queue_ranges': [{'start': '3000', 'end': '3999'}],
                  'conference_room_ranges': [{'start': '4000', 'end': '4999'}],
                  'incall_ranges': [{'start': '1000', 'end': '4999', 'did_length': 2}],
                  'description': 'context description',
                  'enabled': False}

    response = confd.contexts(context['id']).put(**parameters)
    response.assert_updated()

    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.context(name='OriginalName')
def test_edit_name_unavailable(context):
    response = confd.contexts(context['id']).put(name='ModifiedName')
    response.assert_updated()

    response = confd.contexts(context['id']).get()
    assert_that(response.item, has_entries(name=context['name']))


@fixtures.context()
def test_delete(context):
    response = confd.contexts(context['id']).delete()
    response.assert_deleted()
    response = confd.contexts(context['id']).get()
    response.assert_match(404, e.not_found(resource='Context'))


@fixtures.context()
def test_bus_events(context):
    yield s.check_bus_event, 'config.contexts.created', confd.contexts.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.contexts.edited', confd.contexts(context['id']).put
    yield s.check_bus_event, 'config.contexts.deleted', confd.contexts(context['id']).delete
