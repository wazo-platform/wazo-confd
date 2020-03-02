# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.access_feature.event import (
    CreateAccessFeatureEvent,
    DeleteAccessFeatureEvent,
    EditAccessFeatureEvent,
)

from wazo_confd import bus, sysconfd

from .schema import AccessFeatureSchema


class AccessFeatureNotifier:

    schema = AccessFeatureSchema(exclude=['links'])

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def created(self, access_feature):
        self.sysconfd.restart_phoned()
        event = CreateAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)

    def edited(self, access_feature):
        self.sysconfd.restart_phoned()
        event = EditAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)

    def deleted(self, access_feature):
        self.sysconfd.restart_phoned()
        event = DeleteAccessFeatureEvent(self.schema.dump(access_feature))
        self.bus.send_bus_event(event)


def build_notifier():
    return AccessFeatureNotifier(bus, sysconfd)
