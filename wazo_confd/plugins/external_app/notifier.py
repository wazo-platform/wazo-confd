# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
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
        self.bus.send_bus_event(event)

    def edited(self, app):
        app_serialized = ExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = EditExternalAppEvent(app_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, app):
        app_serialized = ExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = DeleteExternalAppEvent(app_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return ExternalAppNotifier(bus)
