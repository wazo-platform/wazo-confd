# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import patch, Mock

from xivo_dao.resources.queue_members import notifier
from xivo_dao.resources.queue_members.model import QueueMemberAgent


class TestQueueMembersNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd_command = {
            'ctibus': [],
            'dird': [],
            'ipbx': [],
            'agentbus': [],
        }

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.queue_members.event.AgentQueueAssociationEditedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_edited(self, send_bus_event, AgentQueueAssociationEditedEvent, exec_request_handler):
        new_event = AgentQueueAssociationEditedEvent.return_value = Mock()
        queue_member = QueueMemberAgent(queue_id=2, agent_id=30, penalty=5)
        self.sysconfd_command['agentbus'] = ['agent.edit.%s' % queue_member.agent_id]

        notifier.agent_queue_association_updated(queue_member)

        AgentQueueAssociationEditedEvent.assert_called_once_with(queue_member.queue_id,
                                                                 queue_member.agent_id,
                                                                 queue_member.penalty)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
        exec_request_handler.assert_called_once_with(self.sysconfd_command)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.queue_members.event.AgentQueueAssociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_associated(self, send_bus_event, AgentQueueAssociatedEvent, exec_request_handler):
        new_event = AgentQueueAssociatedEvent.return_value = Mock()
        queue_member = QueueMemberAgent(queue_id=2, agent_id=30, penalty=5)
        self.sysconfd_command['ctibus'] = ['xivo[queuemember,update]']
        self.sysconfd_command['agentbus'] = ['agent.edit.%s' % queue_member.agent_id]

        notifier.agent_queue_associated(queue_member)

        AgentQueueAssociatedEvent.assert_called_once_with(queue_member.queue_id,
                                                          queue_member.agent_id,
                                                          queue_member.penalty)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

        exec_request_handler.assert_called_once_with(self.sysconfd_command)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.queue_members.event.AgentRemovedFromQueueEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_removed_from_queue(self, send_bus_event, AgentRemovedFromQueueEvent, exec_request_handler):
        agent_id = 104
        queue_id = 25
        new_event = AgentRemovedFromQueueEvent.return_value = Mock()

        self.sysconfd_command['ctibus'] = ['xivo[queuemember,update]']
        self.sysconfd_command['agentbus'] = ['agent.edit.%s' % agent_id]

        notifier.agent_removed_from_queue(agent_id, queue_id)

        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
        exec_request_handler.assert_called_once_with(self.sysconfd_command)
