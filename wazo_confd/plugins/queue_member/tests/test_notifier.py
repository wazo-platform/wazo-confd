# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from mock import Mock, call

from xivo_bus.resources.queue_member.event import (
    QueueMemberAgentAssociatedEvent,
    QueueMemberAgentDissociatedEvent,
    QueueMemberUserAssociatedEvent,
    QueueMemberUserDissociatedEvent,
)
from xivo_bus.resources.agent.event import EditAgentEvent
from ..notifier import QueueMemberNotifier


class TestQueueMemberNotifier(unittest.TestCase):
    def setUp(self):
        tenant_uuid = uuid4()
        self.bus = Mock()
        self.sysconfd = Mock()
        self.queue = Mock(id=1, tenant_uuid=tenant_uuid)
        self.member = Mock(agent=Mock(id=1, tenant_uuid=tenant_uuid), penalty=5)
        self.expected_headers = {'tenant_uuid': str(tenant_uuid)}

        self.notifier = QueueMemberNotifier(self.bus, self.sysconfd)

    def test_agent_associate_then_bus_event(self):
        expected_events = [
            QueueMemberAgentAssociatedEvent(
                self.queue.id, self.member.agent.id, self.member.penalty
            ),
            EditAgentEvent(self.member.agent.id),
        ]

        self.notifier.agent_associated(self.queue, self.member)

        calls = [
            call(expected_events[0], headers=self.expected_headers),
            call(expected_events[1], headers=self.expected_headers),
        ]
        self.bus.send_bus_event.assert_has_calls(calls)

    def test_agent_dissociate_then_bus_event(self):
        expected_events = [
            QueueMemberAgentDissociatedEvent(self.queue.id, self.member.agent.id),
            EditAgentEvent(self.member.agent.id),
        ]

        self.notifier.agent_dissociated(self.queue, self.member)

        calls = [
            call(expected_events[0], headers=self.expected_headers),
            call(expected_events[1], headers=self.expected_headers),
        ]
        self.bus.send_bus_event.assert_has_calls(calls)

    def test_user_associate_then_bus_event(self):
        expected_event = QueueMemberUserAssociatedEvent(
            self.queue.id, self.member.user.id
        )

        self.notifier.user_associated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_user_associate_then_sysconfd_event(self):
        expected_handlers = {
            'ipbx': [
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ],
        }

        self.notifier.user_associated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_user_dissociate_then_bus_event(self):
        expected_event = QueueMemberUserDissociatedEvent(
            self.queue.id, self.member.user.id
        )

        self.notifier.user_dissociated(self.queue, self.member)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_user_dissociate_then_sysconfd_event(self):
        expected_handlers = {
            'ipbx': [
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ],
        }

        self.notifier.user_dissociated(self.queue, self.member)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
