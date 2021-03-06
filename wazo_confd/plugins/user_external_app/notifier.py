# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
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

    def created(self, app):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = CreateUserExternalAppEvent(app_serialized)
        self.bus.send_bus_event(event)

    def edited(self, app):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = EditUserExternalAppEvent(app_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, app):
        app_serialized = UserExternalAppSchema(only=ONLY_FIELDS).dump(app)
        event = DeleteUserExternalAppEvent(app_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserExternalAppNotifier(bus)
