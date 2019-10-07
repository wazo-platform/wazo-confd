# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.call_filter.event import (
    CreateCallFilterEvent,
    DeleteCallFilterEvent,
    EditCallFilterEvent,
)
from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from ..notifier import CallFilterNotifier


class TestCallFilterNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.call_filter = Mock(CallFilter, id=1234)

        self.notifier = CallFilterNotifier(self.bus)

    def test_when_call_filter_created_then_event_sent_on_bus(self):
        expected_event = CreateCallFilterEvent(self.call_filter.id)

        self.notifier.created(self.call_filter)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_filter_edited_then_event_sent_on_bus(self):
        expected_event = EditCallFilterEvent(self.call_filter.id)

        self.notifier.edited(self.call_filter)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_filter_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCallFilterEvent(self.call_filter.id)

        self.notifier.deleted(self.call_filter)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
