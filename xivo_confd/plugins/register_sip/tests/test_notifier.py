# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.register.event import (
    CreateRegisterSIPEvent,
    DeleteRegisterSIPEvent,
    EditRegisterSIPEvent,
)

from ..notifier import RegisterSIPNotifier

EXPECTED_SYSCONFD_HANDLERS = {
    'ctibus': [],
    'ipbx': ['sip reload'],
    'agentbus': []
}


class TestRegisterSIPNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.register_sip = Mock(id=1234)

        self.notifier = RegisterSIPNotifier(self.bus, self.sysconfd)

    def test_when_register_sip_created_then_event_sent_on_bus(self):
        expected_event = CreateRegisterSIPEvent(self.register_sip.id)

        self.notifier.created(self.register_sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_register_sip_edited_then_event_sent_on_bus(self):
        expected_event = EditRegisterSIPEvent(self.register_sip.id)

        self.notifier.edited(self.register_sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_register_sip_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteRegisterSIPEvent(self.register_sip.id)

        self.notifier.deleted(self.register_sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_register_sip_created_then_sip_reloaded(self):
        self.notifier.created(self.register_sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_SYSCONFD_HANDLERS)

    def test_when_register_sip_edited_then_sip_reloaded(self):
        self.notifier.edited(self.register_sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_SYSCONFD_HANDLERS)

    def test_when_register_sip_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.register_sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_SYSCONFD_HANDLERS)
