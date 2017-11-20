# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, has_entries
from ..helpers import associations as a
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from . import confd


FAKE_ID = 999999999


@fixtures.queue()
@fixtures.agent()
def test_associate_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents.post
    yield s.check_resource_not_found, fake_queue, 'Queue'

    url = confd.queues(queue['id']).members.agents.post
    yield s.check_bogus_field_returns_error, url, 'agent_id', FAKE_ID


@fixtures.queue()
@fixtures.agent()
def test_update_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).put
    fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).put
    fake_queue_member = confd.queues(queue['id']).members.agents(agent['id']).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_agent, 'Agent'
    yield s.check_resource_not_found, fake_queue_member, 'QueueMember'


@fixtures.queue()
@fixtures.agent()
def test_dissociate_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).delete
    fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).delete
    fake_queue_member = confd.queues(queue['id']).members.agents(agent['id']).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_agent, 'Agent'
    yield s.check_resource_not_found, fake_queue_member, 'QueueMember'


@fixtures.queue()
@fixtures.agent()
def test_get_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).get
    fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).get
    fake_queue_member = confd.queues(queue['id']).members.agents(agent['id']).get

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_agent, 'Agent'
    yield s.check_resource_not_found, fake_queue_member, 'QueueMember'


@fixtures.queue()
@fixtures.agent()
def test_get(queue, agent):
    with a.queue_member_agent(queue, agent, penalty=5):
        response = confd.queues(queue['id']).members.agents(agent['id']).get()
        assert_that(response.item, has_entries(queue_id=queue['id'],
                                               agent_id=agent['id'],
                                               penalty=5))


@fixtures.queue()
@fixtures.agent()
def test_associate(queue, agent):
    response = confd.queues(queue['id']).members.agents.post(agent_id=agent['id'],
                                                             penalty=7)
    response.assert_created()
    assert_that(response.item, has_entries(agent_id=agent['id'],
                                           queue_id=queue['id'],
                                           penalty=7))


@fixtures.queue()
@fixtures.agent()
def test_associate_when_agent_already_associated_to_same_queue(queue, agent):
    with a.queue_member_agent(queue, agent):
        response = confd.queues(queue['id']).members.agents.post(agent_id=agent['id'])
        response.assert_match(400, e.resource_associated('Agent', 'Queue'))


@fixtures.queue()
@fixtures.agent()
def test_put(queue, agent):
    with a.queue_member_agent(queue, agent, penalty=5):
        response = confd.queues(queue['id']).members.agents(agent['id']).put(penalty=7)
        response.assert_updated()

        response = confd.queues(queue['id']).members.agents(agent['id']).get()
        assert_that(response.item, has_entries(penalty=7))


@fixtures.queue()
@fixtures.agent()
def test_dissociate(queue, agent):
    with a.queue_member_agent(queue, agent, check=False):
        response = confd.queues(queue['id']).members.agents(agent['id']).delete()
        response.assert_deleted()

        response = confd.queues(queue['id']).members.agents(agent['id']).get()
        response.assert_match(404, e.not_found(resource='QueueMember'))
