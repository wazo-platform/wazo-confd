# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from acceptance.features.steps.helpers.rest_agents import RestAgents
from lettuce import step
from lettuce.registry import world

rest_agents = RestAgents()


@step(u'Given there is an agent named "([^"]*)" with number "([^"]*)"')
def given_there_is_an_agent_named_group1_with_number_group2(step, agent_first_name, agent_number):
    rest_agents.create_if_not_exists(agent_first_name, agent_number)


@step(u'When I ask for all agents')
def when_i_ask_for_all_agents(step):
    world.agents_list = rest_agents.list_agents()
    assert (world.agents_list != [])


@step(u'Then there is an agent named "([^"]*)" with number "([^"]*)" in the response')
def then_there_is_an_agent_named_group1_with_number_group2_in_the_response(step, agent_name, agent_number):
    matching_agents = [agent for agent in world.agents_list if agent['firstname'] == agent_name
                       and agent['number'] == agent_number]
    assert len(matching_agents) > 0
