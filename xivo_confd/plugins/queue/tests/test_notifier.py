# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.queue.event import (
    CreateQueueEvent,
    DeleteQueueEvent,
    EditQueueEvent,
)

from ..notifier import QueueNotifier


class TestQueueNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.queue = Mock(id=1234)

        self.notifier = QueueNotifier(self.bus, self.sysconfd)

    def _expected_handlers(self, ctibus_command):
        return {
            'ctibus': [ctibus_command],
            'ipbx': ['module reload app_queue.so'],
            'agentbus': []
        }

    def test_when_queue_created_then_call_expected_handlers(self):
        self.notifier.created(self.queue)

        expected_handlers = self._expected_handlers('xivo[queue,add,1234]')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_queue_created_then_event_sent_on_bus(self):
        expected_event = CreateQueueEvent(self.queue.id)

        self.notifier.created(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_queue_edited_then_app_queue_reloaded(self):
        self.notifier.edited(self.queue)

        expected_handlers = self._expected_handlers('xivo[queue,edit,1234]')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_queue_edited_then_event_sent_on_bus(self):
        expected_event = EditQueueEvent(self.queue.id)

        self.notifier.edited(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_queue_deleted_then_app_queue_reloaded(self):
        self.notifier.deleted(self.queue)

        expected_handlers = self._expected_handlers('xivo[queue,delete,1234]')
        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_queue_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteQueueEvent(self.queue.id)

        self.notifier.deleted(self.queue)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
