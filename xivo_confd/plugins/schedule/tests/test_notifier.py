# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.schedule.event import (CreateScheduleEvent,
                                               EditScheduleEvent,
                                               DeleteScheduleEvent)

from ..notifier import ScheduleNotifier


class TestScheduleNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1234)

        self.notifier = ScheduleNotifier(self.bus)

    def test_when_schedule_created_then_event_sent_on_bus(self):
        expected_event = CreateScheduleEvent(self.schedule.id)

        self.notifier.created(self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_schedule_edited_then_event_sent_on_bus(self):
        expected_event = EditScheduleEvent(self.schedule.id)

        self.notifier.edited(self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_schedule_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteScheduleEvent(self.schedule.id)

        self.notifier.deleted(self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
