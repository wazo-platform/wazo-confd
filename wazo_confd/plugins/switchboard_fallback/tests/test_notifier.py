# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.switchboard.event import EditSwitchboardFallbackEvent
from xivo_dao.alchemy.switchboard import Switchboard

from ..notifier import SwitchboardFallbackNotifier
from ..schema import SwitchboardFallbackSchema


class TestSwitchboardFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.switchboard = Mock(Switchboard, uuid=1)

        self.notifier = SwitchboardFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        event_body = SwitchboardFallbackSchema().dump(self.switchboard)
        expected_event = EditSwitchboardFallbackEvent(event_body)

        self.notifier.edited(self.switchboard)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
