# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.paging.event import (
    CreatePagingEvent,
    DeletePagingEvent,
    EditPagingEvent,
)

from wazo_confd import bus


class PagingNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, paging):
        event = CreatePagingEvent(paging.id)
        self.bus.send_bus_event(event)

    def edited(self, paging):
        event = EditPagingEvent(paging.id)
        self.bus.send_bus_event(event)

    def deleted(self, paging):
        event = DeletePagingEvent(paging.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return PagingNotifier(bus)
