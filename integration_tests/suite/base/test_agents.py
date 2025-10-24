# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    instance_of,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
from . import confd


def test_get_errors():
    fake_agent = confd.agents(999999).get
    s.check_resource_not_found(fake_agent, 'Agent')


def test_delete_errors():
    fake_agent = confd.agents(999999).delete
    s.check_resource_not_found(fake_agent, 'Agent')


def test_post_errors():
    url = confd.agents
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')

    s.check_bogus_field_returns_error(url.post, 'number', 123)
    s.check_bogus_field_returns_error(url.post, 'number', True)
    s.check_bogus_field_returns_error(url.post, 'number', 'invalid')
    s.check_bogus_field_returns_error(url.post, 'number', s.random_string(0))
    s.check_bogus_field_returns_error(url.post, 'number', s.random_string(41))
    s.check_bogus_field_returns_error(url.post, 'number', [])
    s.check_bogus_field_returns_error(url.post, 'number', {})

    unique_error_checks(url.post)


@fixtures.agent()
def test_put_errors(agent):
    url = confd.agents(agent['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'firstname', 123)
    s.check_bogus_field_returns_error(url, 'firstname', True)
    s.check_bogus_field_returns_error(url, 'firstname', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'firstname', [])
    s.check_bogus_field_returns_error(url, 'firstname', {})
    s.check_bogus_field_returns_error(url, 'lastname', 123)
    s.check_bogus_field_returns_error(url, 'lastname', True)
    s.check_bogus_field_returns_error(url, 'lastname', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'lastname', [])
    s.check_bogus_field_returns_error(url, 'lastname', {})
    s.check_bogus_field_returns_error(url, 'password', 123)
    s.check_bogus_field_returns_error(url, 'password', True)
    s.check_bogus_field_returns_error(url, 'password', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'password', [])
    s.check_bogus_field_returns_error(url, 'password', {})
    s.check_bogus_field_returns_error(url, 'language', 123)
    s.check_bogus_field_returns_error(url, 'language', True)
    s.check_bogus_field_returns_error(url, 'language', s.random_string(21))
    s.check_bogus_field_returns_error(url, 'language', [])
    s.check_bogus_field_returns_error(url, 'language', {})
    s.check_bogus_field_returns_error(url, 'description', 123)
    s.check_bogus_field_returns_error(url, 'description', True)
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', True)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(80))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})


@fixtures.agent(number='1234')
def unique_error_checks(url, agent):
    s.check_bogus_field_returns_error(url, 'number', agent['number'])


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
        check_search(url, agent, hidden, field, term)


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
    s.check_sorting(url, agent1, agent2, 'firstname', 'sort')
    s.check_sorting(url, agent1, agent2, 'lastname', 'sort')
    s.check_sorting(url, agent1, agent2, 'preprocess_subroutine', 'sort')

    s.check_offset(url, agent1, agent2, 'firstname', 'sort')

    s.check_limit(url, agent1, agent2, 'firstname', 'sort')


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
    number = '1234'

    response_sub = confd.agents.post(number=number, wazo_tenant=SUB_TENANT)
    response_sub.assert_created('agents')

    assert_that(response_sub.item, has_entries(tenant_uuid=SUB_TENANT))

    response_main = confd.agents.post(number=number, wazo_tenant=MAIN_TENANT)
    response_main.assert_created('agents')

    assert_that(response_main.item, has_entries(tenant_uuid=MAIN_TENANT))

    confd.agents(response_sub.item['id']).delete().assert_deleted()
    confd.agents(response_main.item['id']).delete().assert_deleted()


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


@fixtures.agent(number='1234', wazo_tenant=MAIN_TENANT)
@fixtures.agent(number='1234', wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.agents(main['id']).put(number='1234', wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Agent'))

    response = confd.agents(sub['id']).put(number='1234', wazo_tenant=MAIN_TENANT)
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
    expected_headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'agent_created',
        expected_headers,
        confd.agents.post,
        {'number': '123456789123456789'},
    )
    s.check_event('agent_edited', expected_headers, confd.agents(agent['id']).put)
    s.check_event('agent_deleted', expected_headers, confd.agents(agent['id']).delete)


def test_create_multi_tenant_same_number():
    number = '5678'
    response = confd.agents.post(number=number, wazo_tenant=SUB_TENANT)
    response.assert_created('agents')
    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))

    response = confd.agents.post(number=number, wazo_tenant=SUB_TENANT2)
    response.assert_created('agents')
    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT2))

    response = confd.agents.post(number=number, wazo_tenant=SUB_TENANT2)
    response.assert_match(400, e.resource_exists(resource='Agent'))
