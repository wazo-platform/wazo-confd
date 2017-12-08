# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.endpoint_custom.event import (
    CreateCustomEndpointEvent,
    DeleteCustomEndpointEvent,
    EditCustomEndpointEvent,
)
from xivo_dao.alchemy.usercustom import UserCustom as Custom

from ..notifier import CustomEndpointNotifier


class TestCustomEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.custom_endpoint = Mock(Custom, id=1234, interface='custom/custom')
        self.notifier = CustomEndpointNotifier(self.bus)

    def test_when_custom_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateCustomEndpointEvent(self.custom_endpoint.id,
                                                   self.custom_endpoint.interface)

        self.notifier.created(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditCustomEndpointEvent(self.custom_endpoint.id,
                                                 self.custom_endpoint.interface)

        self.notifier.edited(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCustomEndpointEvent(self.custom_endpoint.id,
                                                   self.custom_endpoint.interface)

        self.notifier.deleted(self.custom_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
