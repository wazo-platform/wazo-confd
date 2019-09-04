# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.access_feature.event import (
    CreateAccessFeatureEvent,
    DeleteAccessFeatureEvent,
    EditAccessFeatureEvent,
)

from wazo_confd import bus

from .schema import AccessFeatureSchema


class AccessFeatureNotifier:

    schema = AccessFeatureSchema(exclude=['links'])

    def __init__(self, bus):
        self.bus = bus

    def created(self, access_feature):
        event = CreateAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)

    def edited(self, access_feature):
        event = EditAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)

    def deleted(self, access_feature):
        event = DeleteAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)


def build_notifier():
    return AccessFeatureNotifier(bus)
