# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_custom.event import CreateCustomEndpointEvent, \
    EditCustomEndpointEvent, DeleteCustomEndpointEvent

from xivo_confd.plugins.endpoint_custom.notifier import CustomEndpointNotifier

from xivo_dao.alchemy.usercustom import UserCustom as Custom


class TestCustomEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.custom_endpoint = Mock(Custom, id=1234, interface='custom/custom')
        self.notifier = CustomEndpointNotifier(self.bus)

    def test_when_custom_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateCustomEndpointEvent(self.custom_endpoint.id,
                                                   self.custom_endpoint.interface)

        self.notifier.created(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_custom_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditCustomEndpointEvent(self.custom_endpoint.id,
                                                 self.custom_endpoint.interface)

        self.notifier.edited(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_custom_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCustomEndpointEvent(self.custom_endpoint.id,
                                                   self.custom_endpoint.interface)

        self.notifier.deleted(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
