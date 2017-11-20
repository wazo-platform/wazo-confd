# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.line.event import CreateLineEvent, \
    EditLineEvent, DeleteLineEvent

from xivo_confd.plugins.line.notifier import LineNotifier

from xivo_dao.alchemy.linefeatures import LineFeatures as Line


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['sip reload', 'dialplan reload', 'module reload chan_sccp.so'],
                     'agentbus': []}


class TestLineNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.line = Mock(Line, id=1234)

        self.notifier = LineNotifier(self.sysconfd, self.bus)

    def test_when_line_created_then_sip_reloaded(self):
        self.notifier.created(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_created_then_event_sent_on_bus(self):
        expected_event = CreateLineEvent(self.line.id)

        self.notifier.created(self.line)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_line_edited_then_sip_reloaded(self):
        updated_fields = ['name']
        self.notifier.edited(self.line, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_edited_and_undefined_change_then_sip_reloaded(self):
        self.notifier.edited(self.line, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_edited_and_no_change_then_sip_not_reloaded(self):
        updated_fields = []
        self.notifier.edited(self.line, updated_fields)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_line_edited_then_event_sent_on_bus(self):
        expected_event = EditLineEvent(self.line.id)

        self.notifier.edited(self.line, None)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_line_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteLineEvent(self.line.id)

        self.notifier.deleted(self.line)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
