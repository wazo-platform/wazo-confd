# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
        self.agent = Mock(Agent, id=1234)

        self.notifier = AgentNotifier(self.bus)

    def test_when_agent_created_then_event_sent_on_bus(self):
        expected_event = CreateAgentEvent(self.agent.id)

        self.notifier.created(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_agent_edited_then_event_sent_on_bus(self):
        expected_event = EditAgentEvent(self.agent.id)

        self.notifier.edited(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_agent_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteAgentEvent(self.agent.id)

        self.notifier.deleted(self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
