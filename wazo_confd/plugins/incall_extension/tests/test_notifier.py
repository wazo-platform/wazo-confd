# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.incall_extension.event import (
    IncallExtensionAssociatedEvent,
    IncallExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall

from ..notifier import IncallExtensionNotifier

SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload']}


class TestIncallExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.incall = Mock(Incall, id=2, tenant_uuid=uuid4())

        self.notifier = IncallExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = IncallExtensionAssociatedEvent(
            self.incall.id, self.extension.id, self.incall.tenant_uuid
        )

        self.notifier.associated(self.incall, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.incall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = IncallExtensionDissociatedEvent(
            self.incall.id, self.extension.id, self.incall.tenant_uuid
        )

        self.notifier.dissociated(self.incall, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.incall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
