# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_filter.event import (
    CallFilterCreatedEvent,
    CallFilterDeletedEvent,
    CallFilterEditedEvent,
)

from wazo_confd import bus


class CallFilterNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, call_filter):
        event = CallFilterCreatedEvent(call_filter.id, call_filter.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, call_filter):
        event = CallFilterEditedEvent(call_filter.id, call_filter.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, call_filter):
        event = CallFilterDeletedEvent(call_filter.id, call_filter.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return CallFilterNotifier(bus)
