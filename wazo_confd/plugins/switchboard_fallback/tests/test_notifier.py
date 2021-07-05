# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.common.event import ArbitraryEvent
from xivo_dao.alchemy.switchboard import Switchboard

from ..notifier import SwitchboardFallbackNotifier
from ..schema import SwitchboardFallbackSchema


class TestSwitchboardFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.switchboard = Mock(Switchboard, uuid=1)

        self.notifier = SwitchboardFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = ArbitraryEvent(
            name='switchboard_fallback_edited',
            body=SwitchboardFallbackSchema().dump(self.switchboard),
            required_acl='switchboards.{uuid}.fallbacks.edited'.format(
                uuid=self.switchboard.uuid
            ),
        )

        self.notifier.edited(self.switchboard)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
