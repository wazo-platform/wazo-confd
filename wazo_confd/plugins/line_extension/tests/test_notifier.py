# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.line_extension.event import (
    LineExtensionAssociatedEvent,
    LineExtensionDissociatedEvent,
)

from ..notifier import LineExtensionNotifier

USER_ID = 1
LINE_ID = 2
SYSCONFD_HANDLERS = {
    'ipbx': [
        'dialplan reload',
        'module reload res_pjsip.so',
        'module reload app_queue.so',
    ]
}


class TestLineExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.line = Mock(id=LINE_ID, tenant_uuid=uuid4())
        self.extension = Mock(id=4)

        self.notifier = LineExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = LineExtensionAssociatedEvent(
            self.line.id, self.extension.id, self.line.tenant_uuid
        )

        self.notifier.associated(self.line, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.line, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = LineExtensionDissociatedEvent(
            self.line.id, self.extension.id, self.line.tenant_uuid
        )

        self.notifier.dissociated(self.line, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.line, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
