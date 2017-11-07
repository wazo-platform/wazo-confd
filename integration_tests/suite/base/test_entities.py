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

from ..test_api import associations as a
from ..test_api import scenarios as s
from ..test_api import errors as e
from ..test_api import fixtures

from hamcrest import (assert_that,
                      contains,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not)
from . import confd


def test_get_errors():
    fake_get = confd.entities(999999).get
    yield s.check_resource_not_found, fake_get, 'Entity'


def test_post_errors():
    url = confd.entities.post
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', 'CAPITAL'
    yield s.check_bogus_field_returns_error, url, 'name', ''
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'display_name', 123
    yield s.check_bogus_field_returns_error, url, 'display_name', {}
    yield s.check_bogus_field_returns_error, url, 'display_name', []
    yield s.check_bogus_field_returns_error, url, 'display_name', s.random_string(2)
    yield s.check_bogus_field_returns_error, url, 'display_name', s.random_string(129)


@fixtures.entity(name="search",
                 display_name="display_search")
@fixtures.entity(name="hidden",
                 display_name="display_hidden")
def test_search(entity, hidden):
    url = confd.entities
    searches = {'name': 'search',
                'display_name': 'search'}

    for field, term in searches.items():
        yield check_search, url, entity, hidden, field, term


def check_search(url, entity, hidden, field, term):
    response = url.get(search=term)

    expected_entity = has_item(has_entry(field, entity[field]))
    hidden_entity = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_entity)
    assert_that(response.items, hidden_entity)

    response = url.get(**{field: entity[field]})

    expected_entity = has_item(has_entry('id', entity['id']))
    hidden_entity = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_entity)
    assert_that(response.items, hidden_entity)


@fixtures.entity(name="sort1", display_name="Sort_1")
@fixtures.entity(name="sort2", display_name="Sort_2")
def test_sorting(entity1, entity2):
    yield check_sorting, entity1, entity2, 'name', 'sort'
    yield check_sorting, entity1, entity2, 'display_name', 'Sort'


def check_sorting(entity1, entity2, field, search):
    response = confd.entities.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=entity1['id']),
                                         has_entries(id=entity2['id'])))

    response = confd.entities.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=entity2['id']),
                                         has_entries(id=entity1['id'])))


@fixtures.entity(name="search", display_name='display_search')
def test_get(entity):
    response = confd.entities(entity['id']).get()
    assert_that(response.item, has_entries(name='search',
                                           display_name='display_search'))


def test_create_minimal_parameters():
    response = confd.entities.post(name='minimal')
    response.assert_created('entities')

    assert_that(response.item, has_entries(name='minimal',
                                           display_name=None))


def test_create_all_parameters():
    parameters = {'name': 'allparameter',
                  'display_name': 'displayallparameter'}

    response = confd.entities.post(**parameters)
    response.assert_created('entities')
    assert_that(response.item, has_entries(parameters))


@fixtures.entity()
def test_create_2_entities_with_same_name(entity):
    response = confd.entities.post(name=entity['name'])
    response.assert_match(400, e.resource_exists('Entity'))


@fixtures.entity()
def test_delete_entity(entity):
    response = confd.entities(entity['id']).delete()
    response.assert_deleted()


@fixtures.entity()
@fixtures.user()
def test_delete_when_user_associated(entity, user):
    with a.user_entity(user, entity, check=False):
        response = confd.entities(entity['id']).delete()
        response.assert_match(400, e.resource_associated('User'))


@fixtures.entity()
@fixtures.call_pickup()
def test_delete_when_call_pickup_associated(entity, call_pickup):
    with a.call_pickup_entity(call_pickup, entity):
        response = confd.entities(entity['id']).delete()
        response.assert_match(400, e.resource_associated('CallPickup'))


@fixtures.entity()
@fixtures.call_filter()
def test_delete_when_call_filter_associated(entity, call_filter):
    with a.call_filter_entity(call_filter, entity):
        response = confd.entities(entity['id']).delete()
        response.assert_match(400, e.resource_associated('CallFilter'))


@fixtures.entity()
@fixtures.context()
def test_delete_when_context_associated(entity, context):
    with a.context_entity(context, entity, check=False):
        response = confd.entities(entity['id']).delete()
        response.assert_match(400, e.resource_associated('Context'))


@fixtures.entity()
@fixtures.schedule()
def test_delete_when_schedule_associated(entity, schedule):
    with a.schedule_entity(schedule, entity):
        response = confd.entities(entity['id']).delete()
        response.assert_match(400, e.resource_associated('Schedule'))


@fixtures.entity()
def test_bus_events(entity):
    yield s.check_bus_event, 'config.entity.created', confd.entities.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.entity.deleted', confd.entities(entity['id']).delete
