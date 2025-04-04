# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.call_filter.event import CallFilterFallbackEditedEvent
from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from ..notifier import CallFilterFallbackNotifier


class TestCallFilterFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.call_filter = Mock(CallFilter, id=1, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.call_filter.tenant_uuid}
        self.notifier = CallFilterFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = CallFilterFallbackEditedEvent(
            self.call_filter.id, self.call_filter.tenant_uuid
        )

        self.notifier.edited(self.call_filter)

        self.bus.queue_event.assert_called_once_with(expected_event)
