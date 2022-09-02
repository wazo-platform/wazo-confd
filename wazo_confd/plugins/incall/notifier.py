# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.incall.event import (
    IncallCreatedEvent,
    IncallDeletedEvent,
    IncallEditedEvent,
)

from wazo_confd import bus


class IncallNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, incall):
        event = IncallCreatedEvent(incall.id, incall.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, incall):
        event = IncallEditedEvent(incall.id, incall.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, incall):
        event = IncallDeletedEvent(incall.id, incall.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return IncallNotifier(bus)
