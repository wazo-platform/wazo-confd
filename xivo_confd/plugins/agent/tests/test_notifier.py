# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.agent.event import (
    CreateAgentEvent,
    DeleteAgentEvent,
    EditAgentEvent,
)
from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from ..notifier import AgentNotifier


class TestAgentNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.agent = Mock(Agent, id=1234)

        self.notifier = AgentNotifier(self.bus, self.sysconfd)

    def _expected_handlers(self, ctibus_command, ipbx_command=None):
        return {
            'ctibus': [ctibus_command],
            'ipbx': [ipbx_command] if ipbx_command else [],
            'agentbus': []
        }

    def test_when_agent_created_then_call_expected_handlers(self):
        self.notifier.created(self.agent)

        expected_handlers = self._expected_handlers('xivo[agent,add,1234]')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_created_then_event_sent_on_bus(self):
        expected_event = CreateAgentEvent(self.agent.id)

        self.notifier.created(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_agent_edited_then_app_agent_reloaded(self):
        self.notifier.edited(self.agent)

        expected_handlers = self._expected_handlers('xivo[agent,edit,1234]')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_edited_then_event_sent_on_bus(self):
        expected_event = EditAgentEvent(self.agent.id)

        self.notifier.edited(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_agent_deleted_then_app_agent_reloaded(self):
        self.notifier.deleted(self.agent)

        expected_handlers = self._expected_handlers('xivo[agent,delete,1234]', 'module reload app_queue.so')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_agent_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteAgentEvent(self.agent.id)

        self.notifier.deleted(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
