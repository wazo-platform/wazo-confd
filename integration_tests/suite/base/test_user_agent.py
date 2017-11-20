# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      not_)

from ..helpers import associations as a
from . import confd
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s

FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).agents.get
    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.agent()
@fixtures.user()
def test_associate_errors(agent, user):
    fake_user = confd.users(FAKE_ID).agents(agent['id']).put
    fake_agent = confd.users(user['id']).agents(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_agent, 'Agent'


@fixtures.user()
def test_dissociate_errors(user):
    fake_user = confd.users(FAKE_ID).agents().delete
    fake_user_agent = confd.users(user['id']).agents.delete

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_user_agent, 'UserAgent'


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


@fixtures.agent()
@fixtures.user()
def test_get_agent_associated_to_user(agent, user):
    expected = has_entries({'user_id': user['id'],
                            'agent_id': agent['id']})

    with a.user_agent(user, agent):
        response = confd.users(user['id']).agents.get()
        assert_that(response.item, expected)

        response = confd.users(user['uuid']).agents.get()
        assert_that(response.item, expected)


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
        response.assert_match(400, e.resource_associated('User', 'Agent'))


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
def test_get_agent_relation(agent, user):
    with a.user_agent(user, agent):
        response = confd.users(user['id']).get()
        assert_that(response.item, has_entries(
            agent=has_entries(id=agent['id'],
                              number=agent['number'])
        ))


@fixtures.agent()
@fixtures.user()
def test_delete_user_when_user_and_agent_associated(agent, user):
    with a.user_agent(user, agent, check=False):
        response = confd.users(user['id']).agents.get()
        assert_that(response.item, not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        invalid_user = confd.users(user['id']).agents.get
        s.check_resource_not_found(invalid_user, 'User')


@fixtures.agent()
@fixtures.user()
def test_bus_events(agent, user):
    url = confd.users(user['id']).agents(agent['id']).put
    yield s.check_bus_event, 'config.users.{}.agents.updated'.format(user['uuid']), url
    url = confd.users(user['id']).agents.delete
    yield s.check_bus_event, 'config.users.{}.agents.deleted'.format(user['uuid']), url
