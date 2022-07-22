# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_external_app.event import (
    UserExternalAppCreatedEvent,
    UserExternalAppDeletedEvent,
    UserExternalAppEditedEvent,
)

from wazo_confd import bus

from .schema import UserExternalAppSchema

ONLY_FIELDS = ['name']


class UserExternalAppNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, app, tenant_uuid):
        payload = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = UserExternalAppCreatedEvent(payload, tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, app, tenant_uuid):
        payload = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = UserExternalAppEditedEvent(payload, tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, app, tenant_uuid):
        payload = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = UserExternalAppDeletedEvent(payload, tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserExternalAppNotifier(bus)
