# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall.event import (
    OutcallCreatedEvent,
    OutcallDeletedEvent,
    OutcallEditedEvent,
)

from wazo_confd import bus


class OutcallNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, outcall):
        event = OutcallCreatedEvent(outcall.id, outcall.tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, outcall):
        event = OutcallEditedEvent(outcall.id, outcall.tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, outcall):
        event = OutcallDeletedEvent(outcall.id, outcall.tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return OutcallNotifier(bus)
