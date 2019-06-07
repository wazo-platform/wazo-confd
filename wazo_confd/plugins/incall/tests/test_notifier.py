# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.incall.event import (
    CreateIncallEvent,
    DeleteIncallEvent,
    EditIncallEvent,
)
from xivo_dao.alchemy.incall import Incall

from ..notifier import IncallNotifier


class TestIncallNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.incall = Mock(Incall, id=1234)

        self.notifier = IncallNotifier(self.bus)

    def test_when_incall_created_then_event_sent_on_bus(self):
        expected_event = CreateIncallEvent(self.incall.id)

        self.notifier.created(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_incall_edited_then_event_sent_on_bus(self):
        expected_event = EditIncallEvent(self.incall.id)

        self.notifier.edited(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_incall_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteIncallEvent(self.incall.id)

        self.notifier.deleted(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
