# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.phone_number.event import (
    PhoneNumberCreatedEvent,
    PhoneNumberDeletedEvent,
    PhoneNumberEditedEvent,
)

from wazo_confd import bus

from .schema import phone_number_schema


class PhoneNumberNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, resource):
        phone_number_serialized = phone_number_schema.dump(resource)
        event = PhoneNumberCreatedEvent(phone_number_serialized, resource.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, resource):
        phone_number_serialized = phone_number_schema.dump(resource)
        event = PhoneNumberEditedEvent(phone_number_serialized, resource.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, resource):
        phone_number_serialized = phone_number_schema.dump(resource)
        event = PhoneNumberDeletedEvent(phone_number_serialized, resource.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return PhoneNumberNotifier(bus)
