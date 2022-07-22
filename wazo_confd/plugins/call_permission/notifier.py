# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_permission.event import (
    CallPermissionCreatedEvent,
    CallPermissionDeletedEvent,
    CallPermissionEditedEvent,
)

from wazo_confd import bus


class CallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, call_permission):
        event = CallPermissionCreatedEvent(
            call_permission.id, call_permission.tenant_uuid
        )
        self.bus.send_bus_event(event)

    def edited(self, call_permission):
        event = CallPermissionEditedEvent(
            call_permission.id, call_permission.tenant_uuid
        )
        self.bus.send_bus_event(event)

    def deleted(self, call_permission):
        event = CallPermissionDeletedEvent(
            call_permission.id, call_permission.tenant_uuid
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return CallPermissionNotifier(bus)
