# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.switchboard.event import EditSwitchboardFallbackEvent
from xivo_dao.alchemy.switchboard import Switchboard

from ..notifier import SwitchboardFallbackNotifier
from ..schema import SwitchboardFallbackSchema


class TestSwitchboardFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.switchboard = Mock(Switchboard, uuid=1, tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.switchboard.tenant_uuid)}

        self.notifier = SwitchboardFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        event_body = SwitchboardFallbackSchema().dump(self.switchboard)
        expected_event = EditSwitchboardFallbackEvent(event_body)

        self.notifier.edited(self.switchboard)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
