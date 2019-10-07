# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_permission.event import (
    CreateCallPermissionEvent,
    DeleteCallPermissionEvent,
    EditCallPermissionEvent,
)

from wazo_confd import bus


class CallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, call_permission):
        event = CreateCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event)

    def edited(self, call_permission):
        event = EditCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event)

    def deleted(self, call_permission):
        event = DeleteCallPermissionEvent(call_permission.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallPermissionNotifier(bus)
