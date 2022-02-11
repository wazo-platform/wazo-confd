# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
import uuid

from xivo_bus.resources.agent_skill.event import (
    AgentSkillAssociatedEvent,
    AgentSkillDissociatedEvent,
)

from ..notifier import AgentSkillNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}


class TestAgentMemberNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.agent = Mock(id=1, tenant_uuid=str(uuid.uuid4()))
        self.agent_skill = Mock(skill=Mock(id=1))
        self.notifier = AgentSkillNotifier(self.bus, self.sysconfd)

    def test_skill_associate_then_call_expected_handlers(self):
        self.notifier.skill_associated(self.agent, self.agent_skill)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_skill_associate_then_bus_event(self):
        expected_event = AgentSkillAssociatedEvent(
            self.agent.id, self.agent_skill.skill.id
        )
        expected_headers = {'tenant_uuid': self.agent.tenant_uuid}

        self.notifier.skill_associated(self.agent, self.agent_skill)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_skill_dissociate_then_call_expected_handlers(self):
        self.notifier.skill_dissociated(self.agent, self.agent_skill)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_skill_dissociate_then_bus_event(self):
        expected_event = AgentSkillDissociatedEvent(
            self.agent.id, self.agent_skill.skill.id
        )
        expected_headers = {'tenant_uuid': self.agent.tenant_uuid}

        self.notifier.skill_dissociated(self.agent, self.agent_skill)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )
