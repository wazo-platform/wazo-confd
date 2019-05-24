# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.device.event import (
    CreateDeviceEvent,
    DeleteDeviceEvent,
    EditDeviceEvent,
)

from xivo_confd import bus


class DeviceNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, device):
        event = CreateDeviceEvent(device.id)
        self.bus.send_bus_event(event)

    def edited(self, device):
        event = EditDeviceEvent(device.id)
        self.bus.send_bus_event(event)

    def deleted(self, device):
        event = DeleteDeviceEvent(device.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return DeviceNotifier(bus)
