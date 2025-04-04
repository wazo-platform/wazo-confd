# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.queue.event import QueueFallbackEditedEvent
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue

from ..notifier import QueueFallbackNotifier


class TestQueueFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.queue = Mock(Queue, id=1, tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.queue.tenant_uuid)}

        self.notifier = QueueFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = QueueFallbackEditedEvent(self.queue.id, self.queue.tenant_uuid)

        self.notifier.edited(self.queue)

        self.bus.queue_event.assert_called_once_with(expected_event)
