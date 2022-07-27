# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.schedule.event import (
    ScheduleCreatedEvent,
    ScheduleDeletedEvent,
    ScheduleEditedEvent,
)

from ..notifier import ScheduleNotifier


class TestScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1234, tenant_uuid=uuid4())

        self.notifier = ScheduleNotifier(self.bus)

    def test_when_schedule_created_then_event_sent_on_bus(self):
        expected_event = ScheduleCreatedEvent(
            self.schedule.id, self.schedule.tenant_uuid
        )

        self.notifier.created(self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_schedule_edited_then_event_sent_on_bus(self):
        expected_event = ScheduleEditedEvent(
            self.schedule.id, self.schedule.tenant_uuid
        )

        self.notifier.edited(self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_schedule_deleted_then_event_sent_on_bus(self):
        expected_event = ScheduleDeletedEvent(
            self.schedule.id, self.schedule.tenant_uuid
        )

        self.notifier.deleted(self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)
