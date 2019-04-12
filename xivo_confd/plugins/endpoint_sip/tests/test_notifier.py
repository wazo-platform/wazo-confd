# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_sip.event import (
    CreateSipEndpointEvent,
    DeleteSipEndpointEvent,
    EditSipEndpointEvent,
)
from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint

from ..notifier import SipEndpointNotifier


SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_pjsip.so', 'dialplan reload'],
    'agentbus': [],
}


class TestSipEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip_endpoint = Mock(SIPEndpoint, id=1234)

        self.notifier = SipEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sip_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.created(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.edited(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.deleted(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
