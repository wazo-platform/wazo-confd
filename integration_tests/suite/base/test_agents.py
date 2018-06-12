# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    is_not,
    instance_of,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)


def test_get_errors():
    fake_agent = confd.agents(999999).get
    yield s.check_resource_not_found, fake_agent, 'Agent'


def test_delete_errors():
    fake_agent = confd.agents(999999).delete
    yield s.check_resource_not_found, fake_agent, 'Agent'


def test_post_errors():
    url = confd.agents.post
    for check in error_checks(url):
        yield check


@fixtures.agent()
def test_put_errors(agent):
    url = confd.agents(agent['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'firstname', 123
    yield s.check_bogus_field_returns_error, url, 'firstname', True
    yield s.check_bogus_field_returns_error, url, 'firstname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'firstname', []
    yield s.check_bogus_field_returns_error, url, 'firstname', {}
    yield s.check_bogus_field_returns_error, url, 'lastname', 123
    yield s.check_bogus_field_returns_error, url, 'lastname', True
    yield s.check_bogus_field_returns_error, url, 'lastname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'lastname', []
    yield s.check_bogus_field_returns_error, url, 'lastname', {}
    yield s.check_bogus_field_returns_error, url, 'number', 123
    yield s.check_bogus_field_returns_error, url, 'number', True
    yield s.check_bogus_field_returns_error, url, 'number', s.random_string(41)
    yield s.check_bogus_field_returns_error, url, 'number', []
    yield s.check_bogus_field_returns_error, url, 'number', {}
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', True
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'password', []
    yield s.check_bogus_field_returns_error, url, 'password', {}
    yield s.check_bogus_field_returns_error, url, 'language', 123
    yield s.check_bogus_field_returns_error, url, 'language', True
    yield s.check_bogus_field_returns_error, url, 'language', s.random_string(21)
    yield s.check_bogus_field_returns_error, url, 'language', []
    yield s.check_bogus_field_returns_error, url, 'language', {}
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', True
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', True
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.agent(number='unique')
def unique_error_checks(url, agent):
    yield s.check_bogus_field_returns_error, url, 'number', agent['number']


@fixtures.agent(firstname='hidden', lastname='hidden', preprocess_subroutine='hidden')
@fixtures.agent(firstname='search', lastname='search', preprocess_subroutine='search')
def test_search(hidden, agent):
    url = confd.agents
    searches = {
        'firstname': 'search',
        'lastname': 'search',
        'preprocess_subroutine': 'search',
    }

    for field, term in searches.items():
        yield check_search, url, agent, hidden, field, term


def check_search(url, agent, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, agent[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: agent[field]})

    expected = has_item(has_entry('id', agent['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.agent(firstname='sort1', lastname='sort1', preprocess_subroutine='sort1')
@fixtures.agent(firstname='sort2', lastname='sort2', preprocess_subroutine='sort2')
def test_sorting_offset_limit(agent1, agent2):
    url = confd.agents.get
    yield s.check_sorting, url, agent1, agent2, 'firstname', 'sort'
    yield s.check_sorting, url, agent1, agent2, 'lastname', 'sort'
    yield s.check_sorting, url, agent1, agent2, 'preprocess_subroutine', 'sort'

    yield s.check_offset, url, agent1, agent2, 'firstname', 'sort'

    yield s.check_limit, url, agent1, agent2, 'firstname', 'sort'


@fixtures.agent()
def test_get(agent):
    response = confd.agents(agent['id']).get()
    assert_that(response.item, has_entries(
        id=agent['id'],
        number=agent['number'],
        firstname=agent['firstname'],
        lastname=agent['lastname'],
        password=agent['password'],
        preprocess_subroutine=agent['preprocess_subroutine'],
        description=agent['description'],
    ))


def test_create_minimal_parameters():
    response = confd.agents.post(number='1234')
    response.assert_created('agents')

    assert_that(response.item, has_entries(
        id=instance_of(int),
        number='1234',
        firstname=None,
        lastname=None,
        password=None,
        preprocess_subroutine=None,
        description=None,
    ))

    confd.agents(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'number': '1234',
        'firstname': 'Firstname',
        'lastname': 'Lastname',
        'password': '5678',
        'preprocess_subroutine': 'subroutine',
        'description': 'description',
    }

    response = confd.agents.post(**parameters)
    response.assert_created('agents')

    assert_that(response.item, has_entries(parameters))

    confd.agents(response.item['id']).delete().assert_deleted()


@fixtures.agent()
def test_edit_minimal_parameters(agent):
    response = confd.agents(agent['id']).put()
    response.assert_updated()


@fixtures.agent()
def test_edit_all_parameters(agent):
    parameters = {
        'number': '1234',
        'firstname': 'Firstname',
        'lastname': 'Lastname',
        'password': '5678',
        'preprocess_subroutine': 'subroutine',
        'description': 'description',
    }

    response = confd.agents(agent['id']).put(**parameters)
    response.assert_updated()

    response = confd.agents(agent['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.agent()
def test_delete(agent):
    response = confd.agents(agent['id']).delete()
    response.assert_deleted()

    response = confd.agents(agent['id']).get()
    response.assert_match(404, e.not_found(resource='Agent'))


@fixtures.agent()
def test_bus_events(agent):
    yield s.check_bus_event, 'config.agent.created', confd.agents.post, {'number': '123456789123456789'}
    yield s.check_bus_event, 'config.agent.edited', confd.agents(agent['id']).put
    yield s.check_bus_event, 'config.agent.deleted', confd.agents(agent['id']).delete
