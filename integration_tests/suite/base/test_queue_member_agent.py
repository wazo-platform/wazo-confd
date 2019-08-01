# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
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


def test_associate_errors():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).put
        fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).put

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_agent, 'Agent')

        url = confd.queues(queue['id']).members.agents(agent['id']).put
        error_checks(url)

        # Legacy
        fake_queue = confd.queues(FAKE_ID).members.agents.post
        s.check_resource_not_found(fake_queue, 'Queue')

        url = confd.queues(queue['id']).members.agents.post
        s.check_bogus_field_returns_error(url, 'agent_id', FAKE_ID)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'penalty', -1)
    s.check_bogus_field_returns_error(url, 'penalty', None)
    s.check_bogus_field_returns_error(url, 'penalty', 'string')
    s.check_bogus_field_returns_error(url, 'penalty', [])
    s.check_bogus_field_returns_error(url, 'penalty', {})
    s.check_bogus_field_returns_error(url, 'priority', -1)
    s.check_bogus_field_returns_error(url, 'priority', None)
    s.check_bogus_field_returns_error(url, 'priority', 'string')
    s.check_bogus_field_returns_error(url, 'priority', [])
    s.check_bogus_field_returns_error(url, 'priority', {})


def test_dissociate_errors():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).delete
        fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).delete

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_agent, 'Agent')



def test_get_errors():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).get
        fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).get
        fake_queue_member = confd.queues(queue['id']).members.agents(agent['id']).get

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_agent, 'Agent')
        s.check_resource_not_found(fake_queue_member, 'QueueMember')



def test_get():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, penalty=5):
            response = confd.queues(queue['id']).members.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                queue_id=queue['id'],
                agent_id=agent['id'],
                penalty=5,
            ))


def test_associate():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        response = confd.queues(queue['id']).members.agents(agent['id']).put(penalty=7, priority=42)
        response.assert_updated()

        confd.queues(queue['id']).members.agents(agent['id']).delete().assert_deleted()

        # Legacy
        response = confd.queues(queue['id']).members.agents.post(agent_id=agent['id'], penalty=7)
        response.assert_created()
        assert_that(response.item, has_entries(
            agent_id=agent['id'],
            queue_id=queue['id'],
            penalty=7,
        ))



def test_update_properties():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, penalty=0, priority=0):
            response = confd.queues(queue['id']).members.agents(agent['id']).put(penalty=41, priority=42)
            response.assert_updated()

            response = confd.queues(queue['id']).get()
            assert_that(response.item, has_entries(
                members=has_entries(
                    agents=contains(has_entries(
                        penalty=41,
                        priority=42,
                    ))
                )
            ))


def test_associate_already_associated():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent):
            response = confd.queues(queue['id']).members.agents(agent['id']).put()
            response.assert_updated()

        # Legacy
        with a.queue_member_agent(queue, agent):
            response = confd.queues(queue['id']).members.agents.post(agent_id=agent['id'])
            response.assert_match(400, e.resource_associated('Agent', 'Queue'))


def test_associate_multiple_agents_to_queue():
    with fixtures.queue() as queue, fixtures.agent() as agent1, fixtures.agent() as agent2:
        with a.queue_member_agent(queue, agent1):
            response = confd.queues(queue['id']).members.agents(agent2['id']).put()
            response.assert_updated()

        confd.queues(queue['id']).members.agents(agent2['id']).delete().assert_deleted()

        # Legacy
        with a.queue_member_agent(queue, agent1):
            response = confd.queues(queue['id']).members.agents.post(agent_id=agent2['id'])
            response.assert_created()


def test_associate_multiple_queues_to_agent():
    with fixtures.queue() as queue1, fixtures.queue() as queue2, fixtures.agent() as agent:
        with a.queue_member_agent(queue1, agent):
            response = confd.queues(queue2['id']).members.agents(agent['id']).put()
            response.assert_updated()

        confd.queues(queue2['id']).members.agents(agent['id']).delete().assert_deleted()

        # Legacy
        with a.queue_member_agent(queue1, agent):
            response = confd.queues(queue2['id']).members.agents.post(agent_id=agent['id'])
            response.assert_created()


def test_associate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.agent(wazo_tenant=MAIN_TENANT) as main_agent, fixtures.agent(wazo_tenant=SUB_TENANT) as sub_agent:
        response = confd.queues(main_queue['id']).members.agents(main_agent['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))

        response = confd.queues(sub_queue['id']).members.agents(main_agent['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Agent'))

        response = confd.queues(main_queue['id']).members.agents(sub_agent['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, check=False):
            response = confd.queues(queue['id']).members.agents(agent['id']).delete()
            response.assert_deleted()

            response = confd.queues(queue['id']).members.agents(agent['id']).get()
            response.assert_match(404, e.not_found(resource='QueueMember'))


def test_dissociate_not_associated():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        response = confd.queues(queue['id']).members.agents(agent['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as queue, fixtures.agent(wazo_tenant=MAIN_TENANT) as agent:
        with a.queue_member_agent(queue, agent, check=False):
            response = confd.queues(queue['id']).members.agents(agent['id']).delete(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('Queue'))


def test_get_queue_relation():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, priority=0, penalty=0):
            response = confd.queues(queue['id']).get()
            assert_that(response.item, has_entries(
                members=has_entries(
                    agents=contains(
                        has_entries(
                            id=agent['id'],
                            number=agent['number'],
                            firstname=agent['firstname'],
                            lastname=agent['lastname'],
                            priority=0,
                            penalty=0,
                            links=agent['links'],
                        )
                    )
                )
            ))


def test_get_agent_relation():
    with fixtures.agent() as agent, fixtures.queue() as queue:
        with a.queue_member_agent(queue, agent, penalty=0):
            response = confd.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                queues=contains(
                    has_entries(
                        id=queue['id'],
                        name=queue['name'],
                        label=queue['label'],
                        penalty=0,
                        links=queue['links'],
                    )
                )
            ))


def test_delete_queue_when_queue_and_agent_associated():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, check=False):
            response = confd.queues(queue['id']).delete()
            response.assert_deleted()


def test_delete_agent_when_queue_and_agent_associated():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        with a.queue_member_agent(queue, agent, check=False):
            response = confd.agents(agent['id']).delete()
            response.assert_deleted()


def test_bus_events():
    with fixtures.queue() as queue, fixtures.agent() as agent:
        url = confd.queues(queue['id']).members.agents(agent['id'])
        s.check_bus_event('config.agent_queue_association.created', url.put)
        s.check_bus_event('config.agent_queue_association.deleted', url.delete)

