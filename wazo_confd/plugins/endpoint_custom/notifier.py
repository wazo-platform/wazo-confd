# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
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
        self.bus.send_bus_event(event)

    def edited(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = EditCustomEndpointEvent(custom_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = DeleteCustomEndpointEvent(custom_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return CustomEndpointNotifier(bus)
