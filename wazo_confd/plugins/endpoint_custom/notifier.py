# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_custom.event import (
    CreateCustomEndpointEvent,
    DeleteCustomEndpointEvent,
    EditCustomEndpointEvent,
)

from wazo_confd import bus

from .schema import CustomSchema

ENDPOINT_CUSTOM_FIELDS = [
    'id',
    'tenant_uuid',
    'interface',
    'trunk.id',
    'line.id',
]


class CustomEndpointNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = CreateCustomEndpointEvent(custom_serialized)
        headers = self._build_headers(custom)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = EditCustomEndpointEvent(custom_serialized)
        headers = self._build_headers(custom)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = DeleteCustomEndpointEvent(custom_serialized)
        headers = self._build_headers(custom)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, custom):
        return {'tenant_uuid': str(custom.tenant_uuid)}


def build_notifier():
    return CustomEndpointNotifier(bus)
