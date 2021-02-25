# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from mock import Mock

from xivo_bus.resources.group_schedule.event import (
    GroupScheduleAssociatedEvent,
    GroupScheduleDissociatedEvent,
)

from ..notifier import GroupScheduleNotifier


class TestGroupScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1)
        self.group = Mock(id=2, uuid=uuid4())

        self.notifier = GroupScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = GroupScheduleAssociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            schedule_id=self.schedule.id,
        )

        self.notifier.associated(self.group, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = GroupScheduleDissociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            schedule_id=self.schedule.id,
        )

        self.notifier.dissociated(self.group, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
