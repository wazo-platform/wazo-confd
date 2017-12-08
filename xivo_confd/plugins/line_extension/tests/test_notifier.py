# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, patch

from xivo_bus.resources.line_extension.event import (
    LineExtensionAssociatedEvent,
    LineExtensionDissociatedEvent,
)

from ..notifier import LineExtensionNotifier

USER_ID = 1
LINE_ID = 2
SYSCONFD_HANDLERS = {'ctibus': ['xivo[phone,edit,{}]'.format(LINE_ID),
                                'xivo[user,edit,{}]'.format(USER_ID)],
                     'ipbx': ['dialplan reload', 'sip reload', 'module reload app_queue.so'],
                     'agentbus': []}


@patch('xivo_dao.resources.user_line.dao.find_all_by_line_id', Mock(return_value=[Mock(user_id=USER_ID)]))
class TestLineExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.line_extension = Mock(line_id=LINE_ID, extension_id=3)

        self.notifier = LineExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = LineExtensionAssociatedEvent(self.line_extension.line_id,
                                                      self.line_extension.extension_id)

        self.notifier.associated(self.line_extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.line_extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = LineExtensionDissociatedEvent(self.line_extension.line_id,
                                                       self.line_extension.extension_id)

        self.notifier.dissociated(self.line_extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.line_extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
