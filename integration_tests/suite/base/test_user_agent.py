# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, empty, has_entries, not_

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999


@fixtures.agent()
@fixtures.user()
def test_associate_errors(agent, user):
    fake_user = confd.users(FAKE_ID).agents(agent['id']).put
    fake_agent = confd.users(user['id']).agents(FAKE_ID).put

    s.check_resource_not_found(fake_user, 'User')
    s.check_resource_not_found(fake_agent, 'Agent')


@fixtures.user()
def test_dissociate_errors(user):
    fake_user = confd.users(FAKE_ID).agents().delete

    s.check_resource_not_found(fake_user, 'User')


@fixtures.agent()
@fixtures.user()
def test_associate_user_agent(agent, user):
    response = confd.users(user['id']).agents(agent['id']).put()
    response.assert_updated()


@fixtures.agent()
@fixtures.user()
def test_associate_using_uuid(agent, user):
    response = confd.users(user['uuid']).agents(agent['id']).put()
    response.assert_updated()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_user, sub_user, main_agent, sub_agent):
    response = (
        confd.users(main_user['uuid'])
        .agents(sub_agent['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('User'))

    response = (
        confd.users(sub_user['uuid'])
        .agents(main_agent['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Agent'))

    response = (
        confd.users(main_user['uuid'])
        .agents(sub_agent['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.agent()
@fixtures.agent()
@fixtures.user()
def test_associate_when_user_already_associated_to_other_agent(agent1, agent2, user):
    with a.user_agent(user, agent1):
        response = confd.users(user['id']).agents(agent2['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Agent'))


@fixtures.agent()
@fixtures.user()
def test_associate_when_user_already_associated_to_same_agent(agent, user):
    with a.user_agent(user, agent):
        response = confd.users(user['id']).agents(agent['id']).put()
        response.assert_updated()


@fixtures.agent()
@fixtures.user()
def test_dissociate(agent, user):
    with a.user_agent(user, agent, check=False):
        response = confd.users(user['id']).agents().delete()
        response.assert_deleted()

    with a.user_agent(user, agent, check=False):
        response = confd.users(user['uuid']).agents().delete()
        response.assert_deleted()


@fixtures.agent()
@fixtures.user()
def test_dissociate_not_associated(agent, user):
    response = confd.users(user['uuid']).agents().delete()
    response.assert_deleted()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=MAIN_TENANT)
def test_dissociate_multi_tenant(user, agent):
    with a.user_agent(user, agent, check=False):
        response = confd.users(user['uuid']).agents().delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))


@fixtures.agent()
@fixtures.user()
def test_get_agent_relation(agent, user):
    with a.user_agent(user, agent):
        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(agent=has_entries(id=agent['id'], number=agent['number'])),
        )


@fixtures.agent()
@fixtures.user()
@fixtures.user()
def test_get_users_relation(agent, user1, user2):
    with a.user_agent(user1, agent), a.user_agent(user2, agent):
        response = confd.agents(agent['id']).get()
        assert_that(
            response.item,
            has_entries(
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
            ),
        )


@fixtures.agent()
@fixtures.user()
def test_delete_user_when_user_and_agent_associated(agent, user):
    with a.user_agent(user, agent, check=False):
        response = confd.agents(agent['id']).get()
        assert_that(response.item['users'], not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        response = confd.agents(agent['id']).get()
        assert_that(response.item['users'], empty())


@fixtures.agent()
@fixtures.user()
def test_bus_events(agent, user):
    headers = {
        'tenant_uuid': user['tenant_uuid'],
        f'user_uuid:{user["uuid"]}': True,
    }

    url = confd.users(user['id']).agents(agent['id']).put
    s.check_event('user_agent_associated', headers, url)

    url = confd.users(user['id']).agents.delete
    s.check_event('user_agent_dissociated', headers, url)
