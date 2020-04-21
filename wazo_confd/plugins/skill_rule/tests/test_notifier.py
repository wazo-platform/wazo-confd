# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.skill_rule.event import (
    CreateSkillRuleEvent,
    DeleteSkillRuleEvent,
    EditSkillRuleEvent,
)

from ..notifier import SkillRuleNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}


class TestSkillRuleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.skill_rule = Mock(id=1234)

        self.notifier = SkillRuleNotifier(self.bus, self.sysconfd)

    def test_when_skill_rule_created_then_call_expected_handlers(self):
        self.notifier.created(self.skill_rule)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_skill_rule_created_then_event_sent_on_bus(self):
        expected_event = CreateSkillRuleEvent(self.skill_rule.id)

        self.notifier.created(self.skill_rule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_skill_rule_edited_then_call_expected_handlers(self):
        self.notifier.edited(self.skill_rule)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_skill_rule_edited_then_event_sent_on_bus(self):
        expected_event = EditSkillRuleEvent(self.skill_rule.id)

        self.notifier.edited(self.skill_rule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_skill_rule_deleted_then_call_expected_handlers(self):
        self.notifier.deleted(self.skill_rule)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_skill_rule_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSkillRuleEvent(self.skill_rule.id)

        self.notifier.deleted(self.skill_rule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
