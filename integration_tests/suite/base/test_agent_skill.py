# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
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
    with fixtures.agent() as agent, fixtures.skill() as skill:
        fake_agent = confd.agents(FAKE_ID).skills(skill['id']).put
        fake_skill = confd.agents(agent['id']).skills(FAKE_ID).put

        s.check_resource_not_found(fake_agent, 'Agent')
        s.check_resource_not_found(fake_skill, 'Skill')

        url = confd.agents(agent['id']).skills(skill['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'skill_weight', -1)
    s.check_bogus_field_returns_error(url, 'skill_weight', None)
    s.check_bogus_field_returns_error(url, 'skill_weight', 'string')
    s.check_bogus_field_returns_error(url, 'skill_weight', [])
    s.check_bogus_field_returns_error(url, 'skill_weight', {})


def test_dissociate_errors():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        fake_agent = confd.agents(FAKE_ID).skills(skill['id']).delete
        fake_skill = confd.agents(agent['id']).skills(FAKE_ID).delete

        s.check_resource_not_found(fake_agent, 'Agent')
        s.check_resource_not_found(fake_skill, 'Skill')



def test_associate():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        response = confd.agents(agent['id']).skills(skill['id']).put(skill_weight=7)
        response.assert_updated()

        confd.agents(agent['id']).skills(skill['id']).delete().assert_deleted()



def test_update_properties():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill, skill_weight=4):
            response = confd.agents(agent['id']).skills(skill['id']).put(skill_weight=5)
            response.assert_updated()

            response = confd.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                skills=contains_inanyorder(has_entries(
                    skill_weight=5,
                ))
            ))


def test_associate_already_associated():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill):
            response = confd.agents(agent['id']).skills(skill['id']).put()
            response.assert_updated()


def test_associate_multiple_skills_to_agent():
    with fixtures.agent() as agent, fixtures.skill() as skill1, fixtures.skill() as skill2:
        with a.agent_skill(agent, skill1):
            response = confd.agents(agent['id']).skills(skill2['id']).put()
            response.assert_updated()

            response = confd.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                skills=contains_inanyorder(
                    has_entries(id=skill1['id']),
                    has_entries(id=skill2['id']),
                )
            ))


def test_associate_multiple_agents_to_skill():
    with fixtures.agent() as agent1, fixtures.agent() as agent2, fixtures.skill() as skill:
        with a.agent_skill(agent1, skill):
            response = confd.agents(agent2['id']).skills(skill['id']).put()
            response.assert_updated()

            response = confd.agents.skills(skill['id']).get()
            assert_that(response.item, has_entries(
                agents=contains_inanyorder(
                    has_entries(id=agent1['id']),
                    has_entries(id=agent2['id']),
                )
            ))


def test_associate_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main_agent, fixtures.agent(wazo_tenant=SUB_TENANT) as sub_agent, fixtures.skill(wazo_tenant=MAIN_TENANT) as main_skill, fixtures.skill(wazo_tenant=SUB_TENANT) as sub_skill:
        response = confd.agents(main_agent['id']).skills(main_skill['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Agent'))

        response = confd.agents(sub_agent['id']).skills(main_skill['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Skill'))

        response = confd.agents(main_agent['id']).skills(sub_skill['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill, check=False):
            response = confd.agents(agent['id']).skills(skill['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        response = confd.agents(agent['id']).skills(skill['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.agent(wazo_tenant=MAIN_TENANT) as main_agent, fixtures.agent(wazo_tenant=SUB_TENANT) as sub_agent, fixtures.skill(wazo_tenant=MAIN_TENANT) as main_skill, fixtures.skill(wazo_tenant=SUB_TENANT) as sub_skill:
        response = confd.agents(main_agent['id']).skills(sub_skill['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Agent'))

        response = confd.agents(sub_agent['id']).skills(main_skill['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Skill'))



def test_get_agent_relation():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill, skill_weight=0):
            response = confd.agents(agent['id']).get()
            assert_that(response.item, has_entries(
                skills=contains_inanyorder(
                    has_entries(
                        id=skill['id'],
                        name=skill['name'],
                        skill_weight=0,
                        links=skill['links'],
                    )
                )
            ))


def test_get_skill_relation():
    with fixtures.skill() as skill, fixtures.agent() as agent:
        with a.agent_skill(agent, skill, skill_weight=0):
            response = confd.agents.skills(skill['id']).get()
            assert_that(response.item, has_entries(
                agents=contains_inanyorder(
                    has_entries(
                        id=agent['id'],
                        number=agent['number'],
                        firstname=agent['firstname'],
                        lastname=agent['lastname'],
                        skill_weight=0,
                        links=agent['links'],
                    )
                )
            ))


def test_delete_agent_when_agent_and_skill_associated():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill, check=False):
            response = confd.agents(agent['id']).delete()
            response.assert_deleted()


def test_delete_skill_when_agent_and_skill_associated():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        with a.agent_skill(agent, skill, check=False):
            response = confd.agents.skills(skill['id']).delete()
            response.assert_deleted()


def test_bus_events():
    with fixtures.agent() as agent, fixtures.skill() as skill:
        url = confd.agents(agent['id']).skills(skill['id'])
        s.check_bus_event('config.agents.skills.updated', url.put)
        s.check_bus_event('config.agents.skills.deleted', url.delete)

