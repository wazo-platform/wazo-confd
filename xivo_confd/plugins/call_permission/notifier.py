# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
