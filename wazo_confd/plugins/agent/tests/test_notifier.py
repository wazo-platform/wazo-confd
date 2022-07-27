# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from xivo_bus.resources.agent.event import (
    AgentCreatedEvent,
    AgentDeletedEvent,
    AgentEditedEvent,
)
from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from ..notifier import AgentNotifier


class TestAgentNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.agent = Mock(Agent, id=1234, tenant_uuid=str(uuid.uuid4()))

        self.notifier = AgentNotifier(self.bus, self.sysconfd)

    def _expected_handlers(self, ipbx_command=None):
        return {'ipbx': [ipbx_command] if ipbx_command else []}

    def test_when_agent_created_then_call_expected_handlers(self):
        self.notifier.created(self.agent)

        expected_handlers = self._expected_handlers('module reload app_queue.so')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_created_then_event_sent_on_bus(self):
        expected_event = AgentCreatedEvent(self.agent.id, self.agent.tenant_uuid)

        self.notifier.created(self.agent)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_agent_edited_then_app_agent_reloaded(self):
        self.notifier.edited(self.agent)

        expected_handlers = self._expected_handlers('module reload app_queue.so')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_edited_then_event_sent_on_bus(self):
        expected_event = AgentEditedEvent(self.agent.id, self.agent.tenant_uuid)

        self.notifier.edited(self.agent)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_agent_deleted_then_app_agent_reloaded(self):
        self.notifier.deleted(self.agent)

        expected_handlers = self._expected_handlers('module reload app_queue.so')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_deleted_then_event_sent_on_bus(self):
        expected_event = AgentDeletedEvent(self.agent.id, self.agent.tenant_uuid)

        self.notifier.deleted(self.agent)

        self.bus.queue_event.assert_called_once_with(expected_event)
