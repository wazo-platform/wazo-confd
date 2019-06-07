# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_sccp.event import (
    CreateSccpEndpointEvent,
    DeleteSccpEndpointEvent,
    EditSccpEndpointEvent,
)
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint

from ..notifier import SccpEndpointNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['module reload chan_sccp.so', 'dialplan reload'],
    'agentbus': [],
}


class TestSccpEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sccp_endpoint = Mock(SCCPEndpoint, id=1234)

        self.notifier = SccpEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sccp_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.created(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sccp_endpoint_edited_then_sccp_reloaded(self):
        self.notifier.edited(self.sccp_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.edited(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sccp_endpoint_deleted_then_sccp_reloaded(self):
        self.notifier.deleted(self.sccp_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.deleted(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
