# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.queue.event import EditQueueFallbackEvent
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue

from ..notifier import QueueFallbackNotifier


class TestQueueFallbackNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.queue = Mock(Queue, id=1)

        self.notifier = QueueFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = EditQueueFallbackEvent(self.queue.id)

        self.notifier.edited(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
