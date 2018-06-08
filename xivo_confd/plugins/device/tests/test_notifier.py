# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.device.event import (
    CreateDeviceEvent,
    DeleteDeviceEvent,
    EditDeviceEvent,
)

from ..notifier import DeviceNotifier
from ..model import Device


class TestDeviceNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.device = Mock(Device, id='abcd1234')
        self.notifier = DeviceNotifier(self.bus)

    def test_when_device_created_then_event_sent_on_bus(self):
        expected_event = CreateDeviceEvent(self.device.id)

        self.notifier.created(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_device_edited_then_event_sent_on_bus(self):
        expected_event = EditDeviceEvent(self.device.id)

        self.notifier.edited(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_device_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteDeviceEvent(self.device.id)

        self.notifier.deleted(self.device)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
