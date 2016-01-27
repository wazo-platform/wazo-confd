# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
