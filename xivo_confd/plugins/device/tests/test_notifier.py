# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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
