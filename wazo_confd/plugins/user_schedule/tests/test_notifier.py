# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.user_schedule.event import (
    UserScheduleAssociatedEvent,
    UserScheduleDissociatedEvent,
)

from ..notifier import UserScheduleNotifier


class TestUserScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1)
        self.user = Mock(id=2)

        self.notifier = UserScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = UserScheduleAssociatedEvent(self.user.id, self.schedule.id)

        self.notifier.associated(self.user, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = UserScheduleDissociatedEvent(self.user.id, self.schedule.id)

        self.notifier.dissociated(self.user, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
