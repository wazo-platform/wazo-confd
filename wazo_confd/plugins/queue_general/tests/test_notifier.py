# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from xivo_bus.resources.queue_general.event import QueueGeneralEditedEvent

from ..notifier import QueueGeneralNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload app_queue.so']}


class TestQueueGeneralNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.queue_general = Mock()
        self.sysconfd = Mock()

        self.notifier = QueueGeneralNotifier(self.bus, self.sysconfd)

    def test_when_queue_general_edited_then_event_sent_on_bus(self):
        expected_event = QueueGeneralEditedEvent()

        self.notifier.edited(self.queue_general)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_queue_general_edited_then_queue_reloaded(self):
        self.notifier.edited(self.queue_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
