# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.paging.event import (
    PagingCreatedEvent,
    PagingDeletedEvent,
    PagingEditedEvent,
)

from ..notifier import PagingNotifier


class TestPagingNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.paging = Mock(id=1234, tenant_uuid=uuid4())

        self.notifier = PagingNotifier(self.bus)

    def test_when_paging_created_then_event_sent_on_bus(self):
        expected_event = PagingCreatedEvent(self.paging.id, self.paging.tenant_uuid)

        self.notifier.created(self.paging)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_paging_edited_then_event_sent_on_bus(self):
        expected_event = PagingEditedEvent(self.paging.id, self.paging.tenant_uuid)

        self.notifier.edited(self.paging)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_paging_deleted_then_event_sent_on_bus(self):
        expected_event = PagingDeletedEvent(self.paging.id, self.paging.tenant_uuid)

        self.notifier.deleted(self.paging)

        self.bus.queue_event.assert_called_once_with(expected_event)
