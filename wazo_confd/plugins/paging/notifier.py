# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(paging)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, paging):
        event = EditPagingEvent(paging.id)
        headers = self._build_headers(paging)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, paging):
        event = DeletePagingEvent(paging.id)
        headers = self._build_headers(paging)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, paging):
        return {'tenant_uuid': str(paging.tenant_uuid)}


def build_notifier():
    return PagingNotifier(bus)
