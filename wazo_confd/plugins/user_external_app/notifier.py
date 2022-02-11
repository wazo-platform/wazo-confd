# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_external_app.event import (
    CreateUserExternalAppEvent,
    DeleteUserExternalAppEvent,
    EditUserExternalAppEvent,
)

from wazo_confd import bus

from .schema import UserExternalAppSchema

ONLY_FIELDS = ['name']


class UserExternalAppNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, app, tenant_uuid):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = CreateUserExternalAppEvent(app_serialized)
        headers = self._build_headers(tenant_uuid)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, app, tenant_uuid):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = EditUserExternalAppEvent(app_serialized)
        headers = self._build_headers(tenant_uuid)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, app, tenant_uuid):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = DeleteUserExternalAppEvent(app_serialized)
        headers = self._build_headers(tenant_uuid)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, tenant_uuid):
        return {'tenant_uuid': str(tenant_uuid)}


def build_notifier():
    return UserExternalAppNotifier(bus)
