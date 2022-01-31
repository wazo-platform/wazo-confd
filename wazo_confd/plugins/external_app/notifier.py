# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.external_app.event import (
    CreateExternalAppEvent,
    DeleteExternalAppEvent,
    EditExternalAppEvent,
)

from wazo_confd import bus

from .schema import ExternalAppSchema

ONLY_FIELDS = ['name']


class ExternalAppNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, app):
        app_serialized = ExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = CreateExternalAppEvent(app_serialized)
        headers = self._build_headers(app)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, app):
        app_serialized = ExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = EditExternalAppEvent(app_serialized)
        headers = self._build_headers(app)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, app):
        app_serialized = ExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = DeleteExternalAppEvent(app_serialized)
        headers = self._build_headers(app)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, app):
        return {'tenant_uuid': str(app.tenant_uuid)}


def build_notifier():
    return ExternalAppNotifier(bus)
