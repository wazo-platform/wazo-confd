# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
from mock import Mock

from xivo_bus.resources.queue_members.event import (AgentQueueAssociatedEvent,
                                                    AgentQueueAssociationEditedEvent,
                                                    AgentRemovedFromQueueEvent)
from xivo_confd.plugins.queue_member.notifier import QueueMemberNotifier
from xivo_confd.helpers.bus_publisher import BusPublisher
from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_dao.resources.queue_members.model import QueueMemberAgent


class TestQueueMemberNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock(BusPublisher)
        self.sysconfd = Mock(SysconfdPublisher)
        self.device_db = Mock()
        self.queue_member = Mock(QueueMemberAgent, agent_id=10, queue_id=100, penalty=5)
        self.notifier = QueueMemberNotifier(self.bus, self.sysconfd)

    def test_when_queue_member_associated_then_event_sent_on_bus(self):
        expected_event = AgentQueueAssociatedEvent(self.queue_member.queue_id,
                                                   self.queue_member.agent_id,
                                                   self.queue_member.penalty)

        self.notifier.associated(self.queue_member)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_queue_member_associated_then_sysconfd_called(self):
        expected_handlers = {'ipbx': [],
                             'agentbus': ['agent.edit.{}'.format(self.queue_member.agent_id)],
                             'ctibus': ['xivo[queuemember,update]']}
        self.notifier.associated(self.queue_member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_queue_member_edited_then_event_sent_on_bus(self):
        expected_event = AgentQueueAssociationEditedEvent(self.queue_member.queue_id,
                                                          self.queue_member.agent_id,
                                                          self.queue_member.penalty)

        self.notifier.edited(self.queue_member)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_queue_member_edited_then_sysconfd_called(self):
        expected_handlers = {'ipbx': [],
                             'agentbus': ['agent.edit.{}'.format(self.queue_member.agent_id)],
                             'ctibus': []}
        self.notifier.edited(self.queue_member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_queue_member_dissociated_then_event_sent_on_bus(self):
        expected_event = AgentRemovedFromQueueEvent(self.queue_member.queue_id,
                                                    self.queue_member.agent_id)

        self.notifier.dissociated(self.queue_member)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_queue_member_dissociated_then_sysconfd_called(self):
        expected_handlers = {'ipbx': [],
                             'agentbus': ['agent.edit.{}'.format(self.queue_member.agent_id)],
                             'ctibus': ['xivo[queuemember,update]']}
        self.notifier.dissociated(self.queue_member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
