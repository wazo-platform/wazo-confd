# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.queue_schedule.event import (
    QueueScheduleAssociatedEvent,
    QueueScheduleDissociatedEvent,
)

from ..notifier import QueueScheduleNotifier


class TestQueueScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1)
        self.queue = Mock(id=2, tenant_uuid=uuid4())

        self.notifier = QueueScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = QueueScheduleAssociatedEvent(
            self.queue.id, self.schedule.id, self.queue.tenant_uuid
        )

        self.notifier.associated(self.queue, self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = QueueScheduleDissociatedEvent(
            self.queue.id, self.schedule.id, self.queue.tenant_uuid
        )

        self.notifier.dissociated(self.queue, self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)
