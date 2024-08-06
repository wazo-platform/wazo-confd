# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.localization.event import LocalizationEditedEvent
from wazo_confd.plugins.localization.schema import LocalizationSchema

from wazo_confd import bus


class LocalizationNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, tenant):
        serialized = LocalizationSchema().dump(tenant)
        event = LocalizationEditedEvent(serialized, tenant.uuid)
        self.bus.queue_event(event)


def build_notifier():
    return LocalizationNotifier(bus)
