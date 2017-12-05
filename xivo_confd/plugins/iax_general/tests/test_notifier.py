# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.iax_general.event import EditIAXGeneralEvent
from xivo_dao.alchemy.staticiax import StaticIAX

from ..notifier import IAXGeneralNotifier

SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['iax2 reload'],
                     'agentbus': []}


class TestIAXGeneralNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.iax_general = Mock(StaticIAX)
        self.sysconfd = Mock()

        self.notifier = IAXGeneralNotifier(self.bus, self.sysconfd)

    def test_when_iax_general_edited_then_event_sent_on_bus(self):
        expected_event = EditIAXGeneralEvent()

        self.notifier.edited(self.iax_general)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_iax_general_edited_then_iax_reloaded(self):
        self.notifier.edited(self.iax_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
