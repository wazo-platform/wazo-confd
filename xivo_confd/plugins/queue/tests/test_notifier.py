# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.queue.event import (
    CreateQueueEvent,
    DeleteQueueEvent,
    EditQueueEvent,
)

from ..notifier import QueueNotifier

EXPECTED_HANDLERS = {
    'ipbx': ['module reload app_queue.so'],
    'agentbus': []
}


class TestQueueNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.queue = Mock(id=1234)

        self.notifier = QueueNotifier(self.bus, self.sysconfd)

    def test_when_queue_created_then_call_expected_handlers(self):
        self.notifier.created(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_created_then_event_sent_on_bus(self):
        expected_event = CreateQueueEvent(self.queue.id)

        self.notifier.created(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_queue_edited_then_app_queue_reloaded(self):
        self.notifier.edited(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_edited_then_event_sent_on_bus(self):
        expected_event = EditQueueEvent(self.queue.id)

        self.notifier.edited(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_queue_deleted_then_app_queue_reloaded(self):
        self.notifier.deleted(self.queue)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_queue_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteQueueEvent(self.queue.id)

        self.notifier.deleted(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
