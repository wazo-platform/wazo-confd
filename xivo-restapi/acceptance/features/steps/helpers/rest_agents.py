# -*- coding: UTF-8 -*-
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from acceptance.features.steps.helpers.ws_utils import WsUtils
from string import upper
from xivo_dao import agent_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_restapi.restapi_config import RestAPIConfig


class RestAgents(object):

    def __init__(self):
        self.ws_utils = WsUtils()

    def create(self, agent_first_name, agent_number):
        agent = AgentFeatures()
        agent.firstname = agent_first_name
        agent.lastname = upper(agent_first_name)
        agent.numgroup = "123"
        agent.number = agent_number
        agent.passwd = agent.number
        agent.context = "default"
        agent.language = 'en_US'
        agent.description = ''
        try:
            agent_dao.add_agent(agent)
        except Exception as e:
            raise e
        return True

    def create_if_not_exists(self, agent_first_name, agent_number):
        try:
            agent_dao.agent_id(agent_number)
            return True
        except LookupError:
            return self.create(agent_first_name, agent_number)
        except Exception as e:
            raise e

    def list_agents(self, agent_id=""):
        url = "%s/%s" % (RestAPIConfig.XIVO_AGENTS_SERVICE_PATH, agent_id)
        reply = self.ws_utils.rest_get(url)
        return reply.data
