# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.paging.event import (
    PagingCreatedEvent,
    PagingDeletedEvent,
    PagingEditedEvent,
)

from wazo_confd import bus


class PagingNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, paging):
        event = PagingCreatedEvent(paging.id, paging.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, paging):
        event = PagingEditedEvent(paging.id, paging.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, paging):
        event = PagingDeletedEvent(paging.id, paging.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return PagingNotifier(bus)
