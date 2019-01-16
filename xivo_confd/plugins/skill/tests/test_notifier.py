# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.skill.event import (
    CreateSkillEvent,
    DeleteSkillEvent,
    EditSkillEvent,
)

from ..notifier import SkillNotifier


class TestSkillNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.skill = Mock(id=1234)

        self.notifier = SkillNotifier(self.bus)

    def test_when_skill_created_then_event_sent_on_bus(self):
        expected_event = CreateSkillEvent(self.skill.id)

        self.notifier.created(self.skill)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_skill_edited_then_event_sent_on_bus(self):
        expected_event = EditSkillEvent(self.skill.id)

        self.notifier.edited(self.skill)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_skill_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSkillEvent(self.skill.id)

        self.notifier.deleted(self.skill)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
