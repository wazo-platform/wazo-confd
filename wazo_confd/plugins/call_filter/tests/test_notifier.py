# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.call_filter.event import (
    CallFilterCreatedEvent,
    CallFilterDeletedEvent,
    CallFilterEditedEvent,
)
from xivo_dao.alchemy.callfilter import Callfilter as CallFilter

from ..notifier import CallFilterNotifier

TENANT_UUID = str(uuid.uuid4())


class TestCallFilterNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.call_filter = Mock(CallFilter, id=1234, tenant_uuid=TENANT_UUID)
        self.notifier = CallFilterNotifier(self.bus)

    def test_when_call_filter_created_then_event_sent_on_bus(self):
        expected_event = CallFilterCreatedEvent(
            self.call_filter.id, self.call_filter.tenant_uuid
        )

        self.notifier.created(self.call_filter)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_call_filter_edited_then_event_sent_on_bus(self):
        expected_event = CallFilterEditedEvent(
            self.call_filter.id, self.call_filter.tenant_uuid
        )

        self.notifier.edited(self.call_filter)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_call_filter_deleted_then_event_sent_on_bus(self):
        expected_event = CallFilterDeletedEvent(
            self.call_filter.id, self.call_filter.tenant_uuid
        )

        self.notifier.deleted(self.call_filter)

        self.bus.queue_event.assert_called_once_with(expected_event)
