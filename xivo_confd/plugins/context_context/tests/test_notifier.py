# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.context_context.event import ContextContextsAssociatedEvent
from xivo_dao.alchemy.context import Context

from ..notifier import ContextContextNotifier


class TestContextContextNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.context = Mock(Context, id=2)
        self.context = Mock(Context, id=1)

        self.notifier = ContextContextNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = ContextContextsAssociatedEvent(self.context.id, [self.context.id])

        self.notifier.associated_contexts(self.context, [self.context])

        self.bus.send_bus_event.assert_called_once_with(expected_event)
