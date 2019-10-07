# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    is_not,
    instance_of,
    all_of,
    not_,
    has_items,
)

from . import confd
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT


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

    yield s.check_bogus_field_returns_error, url, 'number', 123
    yield s.check_bogus_field_returns_error, url, 'number', True
    yield s.check_bogus_field_returns_error, url, 'number', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'number', s.random_string(0)
    yield s.check_bogus_field_returns_error, url, 'number', s.random_string(41)
    yield s.check_bogus_field_returns_error, url, 'number', []
    yield s.check_bogus_field_returns_error, url, 'number', {}

    for check in unique_error_checks(url):
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
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(
        40
    )
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}


@fixtures.agent(number='1234')
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
    assert_that(response.items, has_item(has_entry(field, agent[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: agent[field]})
    assert_that(response.items, has_item(has_entry('id', agent['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.agents.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.agents.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.agents.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


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
    assert_that(
        response.item,
        has_entries(
            id=agent['id'],
            number=agent['number'],
            firstname=agent['firstname'],
            lastname=agent['lastname'],
            password=agent['password'],
            preprocess_subroutine=agent['preprocess_subroutine'],
            description=agent['description'],
            queues=empty(),
            skills=empty(),
            users=empty(),
        ),
    )


@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.agents(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Agent'))

    response = confd.agents(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.agents.post(number='1234')
    response.assert_created('agents')

    assert_that(
        response.item,
        has_entries(
            id=instance_of(int),
            number='1234',
            firstname=None,
            lastname=None,
            password=None,
            preprocess_subroutine=None,
            description=None,
        ),
    )

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


def test_create_multi_tenant():
    response = confd.agents.post(number='1234', wazo_tenant=SUB_TENANT)
    response.assert_created('agents')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


@fixtures.agent()
def test_edit_minimal_parameters(agent):
    response = confd.agents(agent['id']).put()
    response.assert_updated()


@fixtures.agent()
def test_edit_all_parameters(agent):
    parameters = {
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


@fixtures.agent(number='1234')
def test_edit_number_unavailable(agent):
    response = confd.agents(agent['id']).put(number='4567')
    response.assert_updated()

    response = confd.agents(agent['id']).get()
    assert_that(response.item, has_entries(number=agent['number']))


@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.agents(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Agent'))

    response = confd.agents(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.agent()
def test_delete(agent):
    response = confd.agents(agent['id']).delete()
    response.assert_deleted()

    response = confd.agents(agent['id']).get()
    response.assert_match(404, e.not_found(resource='Agent'))


@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.agents(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Agent'))

    response = confd.agents(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.agent()
def test_bus_events(agent):
    yield s.check_bus_event, 'config.agent.created', confd.agents.post, {
        'number': '123456789123456789'
    }
    yield s.check_bus_event, 'config.agent.edited', confd.agents(agent['id']).put
    yield s.check_bus_event, 'config.agent.deleted', confd.agents(agent['id']).delete
