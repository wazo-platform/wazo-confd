# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
)

FAKE_ID = 999999999


@fixtures.agent()
@fixtures.skill()
def test_associate_errors(agent, skill):
    fake_agent = confd.agents(FAKE_ID).skills(skill['id']).put
    fake_skill = confd.agents(agent['id']).skills(FAKE_ID).put

    yield s.check_resource_not_found, fake_agent, 'Agent'
    yield s.check_resource_not_found, fake_skill, 'Skill'

    url = confd.agents(agent['id']).skills(skill['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'skill_weight', -1
    yield s.check_bogus_field_returns_error, url, 'skill_weight', None
    yield s.check_bogus_field_returns_error, url, 'skill_weight', 'string'
    yield s.check_bogus_field_returns_error, url, 'skill_weight', []
    yield s.check_bogus_field_returns_error, url, 'skill_weight', {}


@fixtures.agent()
@fixtures.skill()
def test_dissociate_errors(agent, skill):
    fake_agent = confd.agents(FAKE_ID).skills(skill['id']).delete
    fake_skill = confd.agents(agent['id']).skills(FAKE_ID).delete

    yield s.check_resource_not_found, fake_agent, 'Agent'
    yield s.check_resource_not_found, fake_skill, 'Skill'


@fixtures.agent()
@fixtures.skill()
def test_associate(agent, skill):
    response = confd.agents(agent['id']).skills(skill['id']).put(skill_weight=7)
    response.assert_updated()

    confd.agents(agent['id']).skills(skill['id']).delete().assert_deleted()


@fixtures.agent()
@fixtures.skill()
def test_update_properties(agent, skill):
    with a.agent_skill(agent, skill, skill_weight=4):
        response = confd.agents(agent['id']).skills(skill['id']).put(skill_weight=5)
        response.assert_updated()


@fixtures.agent()
@fixtures.skill()
def test_associate_already_associated(agent, skill):
    with a.agent_skill(agent, skill):
        response = confd.agents(agent['id']).skills(skill['id']).put()
        response.assert_updated()


@fixtures.agent()
@fixtures.skill()
@fixtures.skill()
def test_associate_multiple_skills_to_agent(agent, skill1, skill2):
    with a.agent_skill(agent, skill1):
        response = confd.agents(agent['id']).skills(skill2['id']).put()
        response.assert_updated()


@fixtures.agent()
@fixtures.agent()
@fixtures.skill()
def test_associate_multiple_agents_to_skill(agent1, agent2, skill):
    with a.agent_skill(agent1, skill):
        response = confd.agents(agent2['id']).skills(skill['id']).put()
        response.assert_updated()


@fixtures.agent()
@fixtures.skill()
def test_dissociate(agent, skill):
    with a.agent_skill(agent, skill, check=False):
        response = confd.agents(agent['id']).skills(skill['id']).delete()
        response.assert_deleted()


@fixtures.agent()
@fixtures.skill()
def test_dissociate_not_associated(agent, skill):
    response = confd.agents(agent['id']).skills(skill['id']).delete()
    response.assert_deleted()


@fixtures.agent()
@fixtures.skill()
def test_delete_agent_when_agent_and_skill_associated(agent, skill):
    with a.agent_skill(agent, skill, check=False):
        response = confd.agents(agent['id']).delete()
        response.assert_deleted()


@fixtures.agent()
@fixtures.skill()
def test_delete_skill_when_agent_and_skill_associated(agent, skill):
    with a.agent_skill(agent, skill, check=False):
        response = confd.agents.skills(skill['id']).delete()
        response.assert_deleted()


@fixtures.agent()
@fixtures.skill()
def test_bus_events(agent, skill):
    url = confd.agents(agent['id']).skills(skill['id'])
    yield s.check_bus_event, 'config.agents.skills.updated', url.put
    yield s.check_bus_event, 'config.agents.skills.deleted', url.delete
