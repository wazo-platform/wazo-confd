# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(call_permission)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, call_permission):
        event = EditCallPermissionEvent(call_permission.id)
        headers = self._build_headers(call_permission)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, call_permission):
        event = DeleteCallPermissionEvent(call_permission.id)
        headers = self._build_headers(call_permission)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, call_permission):
        return {'tenant_uuid': str(call_permission.tenant_uuid)}


def build_notifier():
    return CallPermissionNotifier(bus)
