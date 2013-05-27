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


from mock import patch, Mock
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_restapi.rest import flask_http_server, rest_encoder
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.agent_management import AgentManagement
import unittest


class TestAPIAgents(unittest.TestCase):

    def setUp(self):
        self.patcher_agent = patch("xivo_restapi.rest." + \
                             "API_agents.AgentManagement")
        mock_agent = self.patcher_agent.start()
        self.instance_agent_management = Mock(AgentManagement)
        mock_agent.return_value = self.instance_agent_management
        flask_http_server.app.testing = True
        flask_http_server.register_blueprints()
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patcher_agent.stop()

    def test_list_agents(self):
        status = "200 OK"
        agent1 = AgentFeatures()
        agent1.number = '1'
        agent2 = AgentFeatures()
        agent2.number = '2'
        liste = [agent1, agent2]
        self.instance_agent_management.get_all_agents\
                    .return_value = liste
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_AGENTS_SERVICE_PATH + '/',
                              '')

        self.instance_agent_management.get_all_agents\
                    .assert_called_with()
        self.assertEquals(result.status, status)
        liste = sorted(liste, key=lambda k: k.number)
        self.assertEquals(rest_encoder.encode(liste), result.data)

    def test_list_agents_error(self):
        status = "500 INTERNAL SERVER ERROR"

        self.instance_agent_management.get_all_agents.side_effect = Exception
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_AGENTS_SERVICE_PATH + '/',
                              '')

        self.instance_agent_management.get_all_agents\
                    .assert_called_with()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_agent_management.get_all_agents\
                    .side_effect = None
