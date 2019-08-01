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
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


def test_get_errors():
    fake_agent = confd.agents(999999).get
    s.check_resource_not_found(fake_agent, 'Agent')


def test_delete_errors():
    fake_agent = confd.agents(999999).delete
    s.check_resource_not_found(fake_agent, 'Agent')


def test_post_errors():
    url = confd.agents.post
    error_checks(url)

    s.check_bogus_field_returns_error(url, 'number', 123)
    s.check_bogus_field_returns_error(url, 'number', True)
    s.check_bogus_field_returns_error(url, 'number', 'invalid')
    s.check_bogus_field_returns_error(url, 'number', s.random_string(0))
    s.check_bogus_field_returns_error(url, 'number', s.random_string(41))
    s.check_bogus_field_returns_error(url, 'number', [])
    s.check_bogus_field_returns_error(url, 'number', {})

    unique_error_checks(url)


def test_put_errors():
    with fixtures.agent() as agent:
        url = confd.agents(agent['id']).put
        error_checks(url)



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
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})


def unique_error_checks(url):
    with fixtures.agent(number='1234') as agent:
        s.check_bogus_field_returns_error(url, 'number', agent['number'])



def test_search():
    with fixtures.agent(firstname='hidden', lastname='hidden', preprocess_subroutine='hidden') as hidden, fixtures.agent(firstname='search', lastname='search', preprocess_subroutine='search') as agent:
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


def test_list_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main, fixtures.agent(wazo_tenant=SUB_TENANT) as sub:
        response = confd.agents.get(wazo_tenant=MAIN_TENANT)
        assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

        response = confd.agents.get(wazo_tenant=SUB_TENANT)
        assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

        response = confd.agents.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(response.items, has_items(main, sub))



def test_sorting_offset_limit():
    with fixtures.agent(firstname='sort1', lastname='sort1', preprocess_subroutine='sort1') as agent1, fixtures.agent(firstname='sort2', lastname='sort2', preprocess_subroutine='sort2') as agent2:
        url = confd.agents.get
        s.check_sorting(url, agent1, agent2, 'firstname', 'sort')
        s.check_sorting(url, agent1, agent2, 'lastname', 'sort')
        s.check_sorting(url, agent1, agent2, 'preprocess_subroutine', 'sort')

        s.check_offset(url, agent1, agent2, 'firstname', 'sort')

        s.check_limit(url, agent1, agent2, 'firstname', 'sort')



def test_get():
    with fixtures.agent() as agent:
        response = confd.agents(agent['id']).get()
        assert_that(response.item, has_entries(
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
        ))



def test_get_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main, fixtures.agent(wazo_tenant=SUB_TENANT) as sub:
        response = confd.agents(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Agent'))

        response = confd.agents(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



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


def test_create_multi_tenant():
    response = confd.agents.post(number='1234', wazo_tenant=SUB_TENANT)
    response.assert_created('agents')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


def test_edit_minimal_parameters():
    with fixtures.agent() as agent:
        response = confd.agents(agent['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.agent() as agent:
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



def test_edit_number_unavailable():
    with fixtures.agent(number='1234') as agent:
        response = confd.agents(agent['id']).put(number='4567')
        response.assert_updated()

        response = confd.agents(agent['id']).get()
        assert_that(response.item, has_entries(number=agent['number']))



def test_edit_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main, fixtures.agent(wazo_tenant=SUB_TENANT) as sub:
        response = confd.agents(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Agent'))

        response = confd.agents(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.agent() as agent:
        response = confd.agents(agent['id']).delete()
        response.assert_deleted()

        response = confd.agents(agent['id']).get()
        response.assert_match(404, e.not_found(resource='Agent'))



def test_delete_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main, fixtures.agent(wazo_tenant=SUB_TENANT) as sub:
        response = confd.agents(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Agent'))

        response = confd.agents(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.agent() as agent:
        s.check_bus_event('config.agent.created', confd.agents.post, {'number': '123456789123456789'})
        s.check_bus_event('config.agent.edited', confd.agents(agent['id']).put)
        s.check_bus_event('config.agent.deleted', confd.agents(agent['id']).delete)

