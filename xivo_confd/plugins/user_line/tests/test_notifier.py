# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from xivo_bus.resources.user_line.event import UserLineAssociatedEvent, UserLineDissociatedEvent

from ..notifier import UserLineNotifier

EXPECTED_SYSCONFD_HANDLERS = {
    'ctibus': [],
    'ipbx': ['dialplan reload', 'module reload res_pjsip.so'],
    'agentbus': []
}


class TestUserLineNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.user_line = Mock(user_id=1, line_id=2, main_user=True, main_line=True)

        self.notifier = UserLineNotifier(self.bus, self.sysconfd)

    def test_associated_then_bus_event(self):
        expected_event = UserLineAssociatedEvent(self.user_line.user_id,
                                                 self.user_line.line_id,
                                                 self.user_line.main_user,
                                                 self.user_line.main_line)

        self.notifier.associated(self.user_line)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associated_then_sip_reload(self):
        self.notifier.associated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_SYSCONFD_HANDLERS)

    def test_dissociated_then_bus_event(self):
        expected_event = UserLineDissociatedEvent(self.user_line.user_id,
                                                  self.user_line.line_id,
                                                  self.user_line.main_user,
                                                  self.user_line.main_line)

        self.notifier.dissociated(self.user_line)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociated_then_sip_reload(self):
        self.notifier.dissociated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_SYSCONFD_HANDLERS)
