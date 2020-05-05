# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
    empty,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import MAIN_TENANT, SUB_TENANT

FAKE_ID = 999999999


@fixtures.queue()
@fixtures.agent()
def test_associate_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).put
    fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_agent, 'Agent'

    url = confd.queues(queue['id']).members.agents(agent['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'penalty', -1
    yield s.check_bogus_field_returns_error, url, 'penalty', None
    yield s.check_bogus_field_returns_error, url, 'penalty', 'string'
    yield s.check_bogus_field_returns_error, url, 'penalty', []
    yield s.check_bogus_field_returns_error, url, 'penalty', {}
    yield s.check_bogus_field_returns_error, url, 'priority', -1
    yield s.check_bogus_field_returns_error, url, 'priority', None
    yield s.check_bogus_field_returns_error, url, 'priority', 'string'
    yield s.check_bogus_field_returns_error, url, 'priority', []
    yield s.check_bogus_field_returns_error, url, 'priority', {}


@fixtures.queue()
@fixtures.agent()
def test_dissociate_errors(queue, agent):
    fake_queue = confd.queues(FAKE_ID).members.agents(agent['id']).delete
    fake_agent = confd.queues(queue['id']).members.agents(FAKE_ID).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_agent, 'Agent'


@fixtures.queue()
@fixtures.agent()
def test_associate(queue, agent):
    response = (
        confd.queues(queue['id'])
        .members.agents(agent['id'])
        .put(penalty=7, priority=42)
    )
    response.assert_updated()

    confd.queues(queue['id']).members.agents(agent['id']).delete().assert_deleted()


@fixtures.queue()
@fixtures.agent()
def test_update_properties(queue, agent):
    with a.queue_member_agent(queue, agent, penalty=0, priority=0):
        response = (
            confd.queues(queue['id'])
            .members.agents(agent['id'])
            .put(penalty=41, priority=42)
        )
        response.assert_updated()

        response = confd.queues(queue['id']).get()
        assert_that(
            response.item,
            has_entries(
                members=has_entries(
                    agents=contains(has_entries(penalty=41, priority=42))
                )
            ),
        )


@fixtures.queue()
@fixtures.agent()
def test_associate_already_associated(queue, agent):
    with a.queue_member_agent(queue, agent):
        response = confd.queues(queue['id']).members.agents(agent['id']).put()
        response.assert_updated()


@fixtures.queue()
@fixtures.agent()
@fixtures.agent()
def test_associate_multiple_agents_to_queue(queue, agent1, agent2):
    with a.queue_member_agent(queue, agent1):
        response = confd.queues(queue['id']).members.agents(agent2['id']).put()
        response.assert_updated()

    confd.queues(queue['id']).members.agents(agent2['id']).delete().assert_deleted()


@fixtures.queue()
@fixtures.queue()
@fixtures.agent()
def test_associate_multiple_queues_to_agent(queue1, queue2, agent):
    with a.queue_member_agent(queue1, agent):
        response = confd.queues(queue2['id']).members.agents(agent['id']).put()
        response.assert_updated()

    confd.queues(queue2['id']).members.agents(agent['id']).delete().assert_deleted()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.agent(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_queue, sub_queue, main_agent, sub_agent):
    response = (
        confd.queues(main_queue['id'])
        .members.agents(main_agent['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Queue'))

    response = (
        confd.queues(sub_queue['id'])
        .members.agents(main_agent['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Agent'))

    response = (
        confd.queues(main_queue['id'])
        .members.agents(sub_agent['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.queue()
@fixtures.agent()
def test_dissociate(queue, agent):
    with a.queue_member_agent(queue, agent, check=False):
        response = confd.queues(queue['id']).members.agents(agent['id']).delete()
        response.assert_deleted()

        response = confd.queues(queue['id']).get()
        assert_that(response.item['members']['agents'], empty())


@fixtures.queue()
@fixtures.agent()
def test_dissociate_not_associated(queue, agent):
    response = confd.queues(queue['id']).members.agents(agent['id']).delete()
    response.assert_deleted()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.agent(wazo_tenant=MAIN_TENANT)
def test_dissociate_multi_tenant(queue, agent):
    with a.queue_member_agent(queue, agent, check=False):
        response = (
            confd.queues(queue['id'])
            .members.agents(agent['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Queue'))


@fixtures.queue()
@fixtures.agent()
def test_get_queue_relation(queue, agent):
    with a.queue_member_agent(queue, agent, priority=0, penalty=0):
        response = confd.queues(queue['id']).get()
        assert_that(
            response.item,
            has_entries(
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
            ),
        )


@fixtures.agent()
@fixtures.queue()
def test_get_agent_relation(agent, queue):
    with a.queue_member_agent(queue, agent, penalty=0):
        response = confd.agents(agent['id']).get()
        assert_that(
            response.item,
            has_entries(
                queues=contains(
                    has_entries(
                        id=queue['id'],
                        name=queue['name'],
                        label=queue['label'],
                        penalty=0,
                        links=queue['links'],
                    )
                )
            ),
        )


@fixtures.queue()
@fixtures.agent()
def test_delete_queue_when_queue_and_agent_associated(queue, agent):
    with a.queue_member_agent(queue, agent, check=False):
        response = confd.queues(queue['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.agent()
def test_delete_agent_when_queue_and_agent_associated(queue, agent):
    with a.queue_member_agent(queue, agent, check=False):
        response = confd.agents(agent['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.agent()
def test_bus_events(queue, agent):
    url = confd.queues(queue['id']).members.agents(agent['id'])
    yield s.check_bus_event, 'config.agent_queue_association.created', url.put
    yield s.check_bus_event, 'config.agent_queue_association.deleted', url.delete
