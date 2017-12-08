# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

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
        self.group = Mock(id=2)

        self.notifier = GroupScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = GroupScheduleAssociatedEvent(self.group.id, self.schedule.id)

        self.notifier.associated(self.group, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = GroupScheduleDissociatedEvent(self.group.id, self.schedule.id)

        self.notifier.dissociated(self.group, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
