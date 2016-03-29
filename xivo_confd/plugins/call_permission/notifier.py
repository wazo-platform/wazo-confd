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

from xivo_confd import bus

from xivo_bus.resources.call_permission.event import (CreateCallPermissionEvent,
                                                      EditCallPermissionEvent,
                                                      DeleteCallPermissionEvent)


class CallPermissionNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, call_permission):
        event = CreateCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, call_permission):
        event = EditCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, call_permission):
        event = DeleteCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return CallPermissionNotifier(bus)
