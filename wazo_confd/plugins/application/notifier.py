# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.application.event import (
    CreateApplicationEvent,
    DeleteApplicationEvent,
    EditApplicationEvent,
)

from wazo_confd import bus

from .schema import ApplicationSchema

APPLICATION_FIELDS = [
    'uuid',
    'tenant_uuid',
    'name',
    'destination',
    'destination_options',
]


class ApplicationNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, application):
        app_serialized = ApplicationSchema(only=APPLICATION_FIELDS).dump(application)
        event = CreateApplicationEvent(app_serialized)
        headers = self._build_headers(application)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, application):
        app_serialized = ApplicationSchema(only=APPLICATION_FIELDS).dump(application)
        event = EditApplicationEvent(app_serialized)
        headers = self._build_headers(application)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, application):
        app_serialized = ApplicationSchema(only=APPLICATION_FIELDS).dump(application)
        event = DeleteApplicationEvent(app_serialized)
        headers = self._build_headers(application)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, application):
        return {'tenant_uuid': str(application.tenant_uuid)}


def build_notifier():
    return ApplicationNotifier(bus)
