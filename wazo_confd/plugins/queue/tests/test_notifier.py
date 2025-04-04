# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.queue.event import (
    QueueCreatedEvent,
    QueueDeletedEvent,
    QueueEditedEvent,
)

from ..notifier import QueueNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_queue.so']}


class TestQueueNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.queue = Mock(id=1234, tenant_uuid=uuid4())

        self.notifier = QueueNotifier(self.bus, self.sysconfd)

    def test_when_queue_created_then_call_expected_handlers(self):
        self.notifier.created(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_created_then_event_sent_on_bus(self):
        expected_event = QueueCreatedEvent(self.queue.id, self.queue.tenant_uuid)

        self.notifier.created(self.queue)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_queue_edited_then_app_queue_reloaded(self):
        self.notifier.edited(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_edited_then_event_sent_on_bus(self):
        expected_event = QueueEditedEvent(self.queue.id, self.queue.tenant_uuid)

        self.notifier.edited(self.queue)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_queue_deleted_then_app_queue_reloaded(self):
        self.notifier.deleted(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_deleted_then_event_sent_on_bus(self):
        expected_event = QueueDeletedEvent(self.queue.id, self.queue.tenant_uuid)

        self.notifier.deleted(self.queue)

        self.bus.queue_event.assert_called_once_with(expected_event)
