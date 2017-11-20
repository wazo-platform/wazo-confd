# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.device.event import CreateDeviceEvent
from xivo_bus.resources.device.event import EditDeviceEvent
from xivo_bus.resources.device.event import DeleteDeviceEvent


class DeviceNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, device):
        event = CreateDeviceEvent(device.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, device):
        event = EditDeviceEvent(device.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, device):
        event = DeleteDeviceEvent(device.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return DeviceNotifier(bus)
