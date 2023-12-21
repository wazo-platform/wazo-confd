# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.skill.event import (
    SkillCreatedEvent,
    SkillDeletedEvent,
    SkillEditedEvent,
)

from ..notifier import SkillNotifier


class TestSkillNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.skill = Mock(id=1234, tenant_uuid=uuid4())

        self.notifier = SkillNotifier(self.bus)

    def test_when_skill_created_then_event_sent_on_bus(self):
        expected_event = SkillCreatedEvent(self.skill.id, self.skill.tenant_uuid)

        self.notifier.created(self.skill)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_skill_edited_then_event_sent_on_bus(self):
        expected_event = SkillEditedEvent(self.skill.id, self.skill.tenant_uuid)

        self.notifier.edited(self.skill)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_skill_deleted_then_event_sent_on_bus(self):
        expected_event = SkillDeletedEvent(self.skill.id, self.skill.tenant_uuid)

        self.notifier.deleted(self.skill)

        self.bus.queue_event.assert_called_once_with(expected_event)
