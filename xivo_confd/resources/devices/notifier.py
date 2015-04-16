# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers.bus_manager import send_bus_event
from xivo_bus.resources.device.event import CreateDeviceEvent, \
    EditDeviceEvent, DeleteDeviceEvent

def created(device):
    event = CreateDeviceEvent(device.id)
    send_bus_event(event, event.routing_key)


def edited(device):
    event = EditDeviceEvent(device.id)
    send_bus_event(event, event.routing_key)


def deleted(device):
    event = DeleteDeviceEvent(device.id)
    send_bus_event(event, event.routing_key)
