# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_iax.event import (
    CreateIAXEndpointEvent,
    DeleteIAXEndpointEvent,
    EditIAXEndpointEvent,
)
from xivo_dao.alchemy.useriax import UserIAX as IAXEndpoint

from ..notifier import IAXEndpointNotifier


SYSCONFD_HANDLERS = {
    'ipbx': ['iax2 reload'],
    'agentbus': [],
}


class TestIAXEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.iax_endpoint = Mock(IAXEndpoint, id=1234)

        self.notifier = IAXEndpointNotifier(self.sysconfd, self.bus)

    def test_when_iax_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateIAXEndpointEvent(self.iax_endpoint.id)

        self.notifier.created(self.iax_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_iax_endpoint_edited_then_iax_reloaded(self):
        self.notifier.edited(self.iax_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_iax_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditIAXEndpointEvent(self.iax_endpoint.id)

        self.notifier.edited(self.iax_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_iax_endpoint_deleted_then_iax_reloaded(self):
        self.notifier.deleted(self.iax_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_iax_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteIAXEndpointEvent(self.iax_endpoint.id)

        self.notifier.deleted(self.iax_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
