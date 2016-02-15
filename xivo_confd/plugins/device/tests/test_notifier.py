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

from xivo_bus.resources.device.event import CreateDeviceEvent, \
    EditDeviceEvent, DeleteDeviceEvent

from xivo_confd.plugins.device.notifier import DeviceNotifier
from xivo_confd.plugins.device.model import Device


class TestDeviceNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.device = Mock(Device, id='abcd1234')
        self.notifier = DeviceNotifier(self.bus)

    def test_when_device_created_then_event_sent_on_bus(self):
        expected_event = CreateDeviceEvent(self.device.id)

        self.notifier.created(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_device_edited_then_event_sent_on_bus(self):
        expected_event = EditDeviceEvent(self.device.id)

        self.notifier.edited(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_device_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteDeviceEvent(self.device.id)

        self.notifier.deleted(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
