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

from hamcrest import assert_that, has_entries
from ..test_api import associations as a
from ..test_api import scenarios as s
from ..test_api import errors as e
from ..test_api import fixtures
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
