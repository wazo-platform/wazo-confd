# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.incall.event import (
    IncallCreatedEvent,
    IncallDeletedEvent,
    IncallEditedEvent,
)
from xivo_dao.alchemy.incall import Incall

from ..notifier import IncallNotifier


class TestIncallNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.incall = Mock(Incall, id=1234, tenant_uuid=uuid4())

        self.notifier = IncallNotifier(self.bus)

    def test_when_incall_created_then_event_sent_on_bus(self):
        expected_event = IncallCreatedEvent(self.incall.id, self.incall.tenant_uuid)

        self.notifier.created(self.incall)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_incall_edited_then_event_sent_on_bus(self):
        expected_event = IncallEditedEvent(self.incall.id, self.incall.tenant_uuid)

        self.notifier.edited(self.incall)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_incall_deleted_then_event_sent_on_bus(self):
        expected_event = IncallDeletedEvent(self.incall.id, self.incall.tenant_uuid)

        self.notifier.deleted(self.incall)

        self.bus.queue_event.assert_called_once_with(expected_event)
