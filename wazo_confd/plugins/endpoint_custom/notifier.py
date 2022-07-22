# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_custom.event import (
    CustomEndpointCreatedEvent,
    CustomEndpointDeletedEvent,
    CustomEndpointEditedEvent,
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
        event = CustomEndpointCreatedEvent(custom_serialized, custom.tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = CustomEndpointEditedEvent(custom_serialized, custom.tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, custom):
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(custom)
        event = CustomEndpointDeletedEvent(custom_serialized, custom.tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return CustomEndpointNotifier(bus)
