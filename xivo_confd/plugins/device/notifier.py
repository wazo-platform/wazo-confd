# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
