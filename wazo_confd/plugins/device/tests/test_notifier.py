# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.device.event import (
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceEditedEvent,
)

from ..model import Device
from ..notifier import DeviceNotifier


class TestDeviceNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.device = Mock(Device, id='abcd1234', tenant_uuid=str(uuid4()))
        self.notifier = DeviceNotifier(self.bus)

    def test_when_device_created_then_event_sent_on_bus(self):
        expected_event = DeviceCreatedEvent(self.device.id, self.device.tenant_uuid)

        self.notifier.created(self.device)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_device_edited_then_event_sent_on_bus(self):
        expected_event = DeviceEditedEvent(self.device.id, self.device.tenant_uuid)

        self.notifier.edited(self.device)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_device_deleted_then_event_sent_on_bus(self):
        expected_event = DeviceDeletedEvent(self.device.id, self.device.tenant_uuid)

        self.notifier.deleted(self.device)

        self.bus.queue_event.assert_called_once_with(expected_event)
