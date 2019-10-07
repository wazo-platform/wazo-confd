# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.incall_schedule.event import (
    IncallScheduleAssociatedEvent,
    IncallScheduleDissociatedEvent,
)
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.schedule import Schedule

from ..notifier import IncallScheduleNotifier


class TestIncallScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(Schedule, id=1)
        self.incall = Mock(Incall, id=2)

        self.notifier = IncallScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = IncallScheduleAssociatedEvent(self.incall.id, self.schedule.id)

        self.notifier.associated(self.incall, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = IncallScheduleDissociatedEvent(
            self.incall.id, self.schedule.id
        )

        self.notifier.dissociated(self.incall, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
