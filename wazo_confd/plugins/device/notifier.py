# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.device.event import (
    CreateDeviceEvent,
    DeleteDeviceEvent,
    EditDeviceEvent,
)

from wazo_confd import bus


class DeviceNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, device):
        event = CreateDeviceEvent(device.id)
        headers = self._build_headers(device)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, device):
        event = EditDeviceEvent(device.id)
        headers = self._build_headers(device)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, device):
        event = DeleteDeviceEvent(device.id)
        headers = self._build_headers(device)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, device):
        return {'tenant_uuid': str(device.tenant_uuid)}


def build_notifier():
    return DeviceNotifier(bus)
