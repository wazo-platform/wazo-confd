# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.access_feature.event import (
    AccessFeatureCreatedEvent,
    AccessFeatureDeletedEvent,
    AccessFeatureEditedEvent,
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
        event = AccessFeatureCreatedEvent(self.schema.dump(access_feature))
        self.bus.queue_event(event)

    def edited(self, access_feature):
        self.sysconfd.restart_phoned()
        event = AccessFeatureEditedEvent(self.schema.dump(access_feature))
        self.bus.queue_event(event)

    def deleted(self, access_feature):
        self.sysconfd.restart_phoned()
        event = AccessFeatureDeletedEvent(self.schema.dump(access_feature))
        self.bus.queue_event(event)


def build_notifier():
    return AccessFeatureNotifier(bus, sysconfd)
