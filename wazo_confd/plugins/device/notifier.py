# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.device.event import (
    DeviceCreatedEvent,
    DeviceDeletedEvent,
    DeviceEditedEvent,
)

from wazo_confd import bus


class DeviceNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, device):
        event = DeviceCreatedEvent(device.id, device.tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, device):
        event = DeviceEditedEvent(device.id, device.tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, device):
        event = DeviceDeletedEvent(device.id, device.tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return DeviceNotifier(bus)
