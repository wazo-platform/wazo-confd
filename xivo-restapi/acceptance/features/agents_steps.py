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

from acceptance.features.rest_agents import RestAgents
from lettuce import step

rest_agents = RestAgents()
agents_dict = {}
agent_with_number = None

@step(u'Given there is an agent named "([^"]*)" with number "([^"]*)"')
def given_there_is_an_agent_named_group1_with_number_group2(step, agent_first_name, agent_number):
    rest_agents.create_if_not_exists(agent_first_name, agent_number)


@step(u'When I ask for all agents')
def when_i_ask_for_all_agents(step):
    global agents_dict
    agents_dict = rest_agents.list()
    assert (agents_dict['total'] > 0)


@step(u'Then there is an agent named "([^"]*)" with number "([^"]*)" in the response')
def then_there_is_an_agent_named_group1_with_number_group2_in_the_response(step, group1, group2):
    global agents_dict
    rest_agents.check_agent_in_list(agents_dict)


@step(u'When I ask for agent with number "([^"]*)"')
def when_i_ask_for_agent_with_number_group1(step, number):
    global agent_with_number
    agent_with_number = rest_agents.get_by_number(number)


@step(u'Then I get agent named "([^"]*)"')
def then_i_get_agent_named_group1(step, name):
    global agent_with_number
    agent_with_number.name = name
