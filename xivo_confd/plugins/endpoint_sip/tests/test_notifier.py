# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_sip.event import CreateSipEndpointEvent, \
    EditSipEndpointEvent, DeleteSipEndpointEvent

from xivo_confd.plugins.endpoint_sip.notifier import SipEndpointNotifier

from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['sip reload', 'dialplan reload'],
                     'agentbus': []}


class TestSipEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip_endpoint = Mock(SIPEndpoint, id=1234)

        self.notifier = SipEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sip_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.created(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_sip_endpoint_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.edited(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_sip_endpoint_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSipEndpointEvent(self.sip_endpoint.id)

        self.notifier.deleted(self.sip_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
