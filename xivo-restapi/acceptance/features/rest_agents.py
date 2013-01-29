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

from xivo_dao import agent_dao
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_restapi.restapi_config import RestAPIConfig
from acceptance.features.ws_utils import WsUtils
from string import upper


class RestAgents:

    def __init__(self):
        self.agent = AgentFeatures()
        self.ws_utils = WsUtils()

    def create(self, agent_first_name, agent_number):
        print "name:" + agent_first_name
        print "number:" + agent_number

        self.agent.firstname = agent_first_name
        self.agent.lastname = upper(agent_first_name)
        self.agent.numgroup = "123"
        self.agent.number = agent_number
        self.agent.passwd = self.agent.number
        self.agent.context = "default"
        self.agent.language = 'en_US'
        self.agent.description = ''
        try:
            agent_dao.add_agent(self.agent)
        except Exception as e:
            print "Test precondition failed, got exception: ", e
            raise e
        return True

    def create_if_not_exists(self, agent_first_name, agent_number):
        try:
            agent_dao.agent_id(agent_number)
            return True
        except LookupError:
            return self.create(agent_first_name, agent_number)
        except Exception as e:
            print "Test precondition failed, got exception: ", e
            raise e

    def list(self, agent_id=""):
        reply = self.ws_utils.rest_get(RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + \
                                       "/" + agent_id)
        return reply.data

    def get_by_number(self, agent_number):
        reply = self.ws_utils.rest_get(RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + \
                                       "?agent_number=" + str(agent_number))
        return reply.data

    def check_agent_in_list(self, agents_list):
        assert "this method must be implemented" == True  #return in agents_list
