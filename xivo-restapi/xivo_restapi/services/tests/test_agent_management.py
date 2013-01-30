

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

from mock import Mock
from xivo_dao import agent_dao
import unittest


class SampleClass:
    pass


class TestAgentManagement(unittest.TestCase):

    def setUp(self):
        from xivo_restapi.services.agent_management import AgentManagement
        self._agentManager = AgentManagement()

    def test_get_all_queues(self):
        agent_dao.all = Mock()
        data = []
        expected_result = []
        i = 0
        while(i < 3):
            obj = SampleClass()
            obj.att1 = 'val1-' + str(i)
            obj.att2 = 'val2-' + str(i)
            obj.att3 = 'val3-' + str(i)
            item = {}
            item['att1'] = 'val1-' + str(i)
            item['att2'] = 'val2-' + str(i)
            item['att3'] = 'val3-' + str(i)
            data.append(obj)
            expected_result.append(item)
            i += 1

        agent_dao.all.return_value = data
        result = self._agentManager.get_all_agents()
        self.assertTrue(result == expected_result)
