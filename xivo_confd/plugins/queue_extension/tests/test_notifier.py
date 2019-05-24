# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.queue_extension.event import (
    QueueExtensionAssociatedEvent,
    QueueExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue

from ..notifier import QueueExtensionNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['dialplan reload'],
    'agentbus': [],
}


class TestQueueExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.queue = Mock(Queue, id=2)

        self.notifier = QueueExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = QueueExtensionAssociatedEvent(self.queue.id, self.extension.id)

        self.notifier.associated(self.queue, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.queue, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = QueueExtensionDissociatedEvent(self.queue.id, self.extension.id)

        self.notifier.dissociated(self.queue, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.queue, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
