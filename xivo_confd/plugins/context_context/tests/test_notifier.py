# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.context_context.event import ContextContextsAssociatedEvent
from xivo_dao.alchemy.context import Context

from ..notifier import ContextContextNotifier

EXPECTED_HANDLERS = {
    'ctibus': [],
    'ipbx': ['dialplan reload'],
    'agentbus': [],
}


class TestContextContextNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.context = Mock(Context, id=2)
        self.context = Mock(Context, id=1)

        self.notifier = ContextContextNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ContextContextsAssociatedEvent(self.context.id, [self.context.id])

        self.notifier.associated_contexts(self.context, [self.context])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated_contexts(self.context, [self.context])

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)
