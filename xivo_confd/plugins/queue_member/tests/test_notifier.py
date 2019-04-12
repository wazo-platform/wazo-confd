# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.queue_member.event import (
    QueueMemberAgentAssociatedEvent,
    QueueMemberAgentDissociatedEvent,
    QueueMemberUserAssociatedEvent,
    QueueMemberUserDissociatedEvent,
)

from ..notifier import QueueMemberNotifier


class TestQueueMemberNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.queue = Mock(id=1)
        self.member = Mock(agent=Mock(id=1), penalty=5)
        self.notifier = QueueMemberNotifier(self.bus, self.sysconfd)

    def test_agent_associate_then_bus_event(self):
        expected_event = QueueMemberAgentAssociatedEvent(
            self.queue.id,
            self.member.agent.id,
            self.member.penalty,
        )

        self.notifier.agent_associated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_agent_associate_then_sysconfd_event(self):
        expected_handlers = {
            'ipbx': [],
            'agentbus': ['agent.edit.{}'.format(self.member.agent.id)],
        }

        self.notifier.agent_associated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_agent_dissociate_then_bus_event(self):
        expected_event = QueueMemberAgentDissociatedEvent(self.queue.id, self.member.agent.id)

        self.notifier.agent_dissociated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_agent_dissociate_then_sysconfd_event(self):
        expected_handlers = {
            'ipbx': [],
            'agentbus': ['agent.edit.{}'.format(self.member.agent.id)],
        }

        self.notifier.agent_dissociated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_user_associate_then_bus_event(self):
        expected_event = QueueMemberUserAssociatedEvent(self.queue.id, self.member.user.id)

        self.notifier.user_associated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_user_associate_then_sysconfd_event(self):
        expected_handlers = {
            'agentbus': [],
            'ipbx': ['module reload res_pjsip.so', 'module reload app_queue.so', 'module reload chan_sccp.so'],
        }

        self.notifier.user_associated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_user_dissociate_then_bus_event(self):
        expected_event = QueueMemberUserDissociatedEvent(self.queue.id, self.member.user.id)

        self.notifier.user_dissociated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_user_dissociate_then_sysconfd_event(self):
        expected_handlers = {
            'agentbus': [],
            'ipbx': ['module reload res_pjsip.so', 'module reload app_queue.so', 'module reload chan_sccp.so'],
        }

        self.notifier.user_dissociated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
