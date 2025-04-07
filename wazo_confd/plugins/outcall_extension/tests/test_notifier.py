# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.outcall_extension.event import (
    OutcallExtensionAssociatedEvent,
    OutcallExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.outcall import Outcall

from ..notifier import OutcallExtensionNotifier

SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload']}


class TestOutcallExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.outcall = Mock(Outcall, id=2, tenant_uuid=uuid4())

        self.notifier = OutcallExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = OutcallExtensionAssociatedEvent(
            self.outcall.id, self.extension.id, self.outcall.tenant_uuid
        )

        self.notifier.associated(self.outcall, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.outcall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = OutcallExtensionDissociatedEvent(
            self.outcall.id, self.extension.id, self.outcall.tenant_uuid
        )

        self.notifier.dissociated(self.outcall, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.outcall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
