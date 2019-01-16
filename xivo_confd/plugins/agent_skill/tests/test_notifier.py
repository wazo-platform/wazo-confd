# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.agent_skill.event import (
    AgentSkillAssociatedEvent,
    AgentSkillDissociatedEvent,
)

from ..notifier import AgentSkillNotifier


class TestAgentMemberNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.agent = Mock(id=1)
        self.agent_skill = Mock(skill=Mock(id=1))
        self.notifier = AgentSkillNotifier(self.bus)

    def test_skill_associate_then_bus_event(self):
        expected_event = AgentSkillAssociatedEvent(self.agent.id, self.agent_skill.skill.id)

        self.notifier.skill_associated(self.agent, self.agent_skill)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_skill_dissociate_then_bus_event(self):
        expected_event = AgentSkillDissociatedEvent(self.agent.id, self.agent_skill.skill.id)

        self.notifier.skill_dissociated(self.agent, self.agent_skill)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
