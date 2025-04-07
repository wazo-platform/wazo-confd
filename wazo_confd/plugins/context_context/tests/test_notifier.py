# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.context_context.event import ContextContextsAssociatedEvent
from xivo_dao.alchemy.context import Context

from ..notifier import ContextContextNotifier

EXPECTED_HANDLERS = {'ipbx': ['dialplan reload']}


class TestContextContextNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.context = Mock(Context, id=2)
        self.context = Mock(Context, id=1, tenant_uuid=str(uuid4()))

        self.notifier = ContextContextNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ContextContextsAssociatedEvent(
            self.context.id, [self.context.id], self.context.tenant_uuid
        )

        self.notifier.associated_contexts(self.context, [self.context])

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated_contexts(self.context, [self.context])

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)
