# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    has_entries,
    not_,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).agents.get
    s.check_resource_not_found(fake_user, 'User')


def test_associate_errors():
    with fixtures.agent() as agent, fixtures.user() as user:
        fake_user = confd.users(FAKE_ID).agents(agent['id']).put
        fake_agent = confd.users(user['id']).agents(FAKE_ID).put

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_agent, 'Agent')



def test_dissociate_errors():
    with fixtures.user() as user:
        fake_user = confd.users(FAKE_ID).agents().delete

        s.check_resource_not_found(fake_user, 'User')



def test_associate_user_agent():
    with fixtures.agent() as agent, fixtures.user() as user:
        response = confd.users(user['id']).agents(agent['id']).put()
        response.assert_updated()



def test_associate_using_uuid():
    with fixtures.agent() as agent, fixtures.user() as user:
        response = confd.users(user['uuid']).agents(agent['id']).put()
        response.assert_updated()



def test_associate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user, fixtures.agent(wazo_tenant=MAIN_TENANT) as main_agent, fixtures.agent(wazo_tenant=SUB_TENANT) as sub_agent:
        response = confd.users(main_user['uuid']).agents(sub_agent['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).agents(main_agent['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Agent'))

        response = confd.users(main_user['uuid']).agents(sub_agent['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_get_agent_associated_to_user():
    with fixtures.agent() as agent, fixtures.user() as user:
        expected = has_entries({'user_id': user['id'],
                                'agent_id': agent['id']})

        with a.user_agent(user, agent):
            response = confd.users(user['id']).agents.get()
            assert_that(response.item, expected)

            response = confd.users(user['uuid']).agents.get()
            assert_that(response.item, expected)



def test_associate_when_user_already_associated_to_other_agent():
    with fixtures.agent() as agent1, fixtures.agent() as agent2, fixtures.user() as user:
        with a.user_agent(user, agent1):
            response = confd.users(user['id']).agents(agent2['id']).put()
            response.assert_match(400, e.resource_associated('User', 'Agent'))


def test_associate_when_user_already_associated_to_same_agent():
    with fixtures.agent() as agent, fixtures.user() as user:
        with a.user_agent(user, agent):
            response = confd.users(user['id']).agents(agent['id']).put()
            response.assert_updated()


def test_dissociate():
    with fixtures.agent() as agent, fixtures.user() as user:
        with a.user_agent(user, agent, check=False):
            response = confd.users(user['id']).agents().delete()
            response.assert_deleted()

        with a.user_agent(user, agent, check=False):
            response = confd.users(user['uuid']).agents().delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.agent() as agent, fixtures.user() as user:
        response = confd.users(user['uuid']).agents().delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as user, fixtures.agent(wazo_tenant=MAIN_TENANT) as agent:
        with a.user_agent(user, agent, check=False):
            response = confd.users(user['uuid']).agents().delete(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('User'))


def test_get_agent_relation():
    with fixtures.agent() as agent, fixtures.user() as user:
        with a.user_agent(user, agent):
            response = confd.users(user['id']).get()
            assert_that(response.item, has_entries(
                agent=has_entries(id=agent['id'],
                                  number=agent['number'])
            ))


def test_get_users_relation():
    with fixtures.agent() as agent, fixtures.user() as user1, fixtures.user() as user2:
        with a.user_agent(user1, agent), a.user_agent(user2, agent):
            response = confd.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                users=contains_inanyorder(
                    has_entries(
                        uuid=user1['uuid'],
                        firstname=user1['firstname'],
                        lastname=user1['lastname'],
                    ),
                    has_entries(
                        uuid=user2['uuid'],
                        firstname=user2['firstname'],
                        lastname=user2['lastname'],
                    ),
                )
            ))


def test_delete_user_when_user_and_agent_associated():
    with fixtures.agent() as agent, fixtures.user() as user:
        with a.user_agent(user, agent, check=False):
            response = confd.users(user['id']).agents.get()
            assert_that(response.item, not_(empty()))
            confd.users(user['id']).delete().assert_deleted()
            invalid_user = confd.users(user['id']).agents.get
            s.check_resource_not_found(invalid_user, 'User')


def test_bus_events():
    with fixtures.agent() as agent, fixtures.user() as user:
        url = confd.users(user['id']).agents(agent['id']).put
        s.check_bus_event('config.users.{}.agents.updated'.format(user['uuid']), url)
        url = confd.users(user['id']).agents.delete
        s.check_bus_event('config.users.{}.agents.deleted'.format(user['uuid']), url)

