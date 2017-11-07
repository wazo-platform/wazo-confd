# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.queue_members.event import (AgentQueueAssociatedEvent,
                                                    AgentQueueAssociationEditedEvent,
                                                    AgentRemovedFromQueueEvent)
from xivo_confd.plugins.queue_member.notifier import QueueMemberNotifier
from xivo_dao.resources.queue_members.model import QueueMemberAgent


class TestQueueMemberNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
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
