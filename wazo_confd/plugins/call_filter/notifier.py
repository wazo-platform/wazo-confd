# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_filter.event import (
    CreateCallFilterEvent,
    DeleteCallFilterEvent,
    EditCallFilterEvent,
)

from wazo_confd import bus


class CallFilterNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, call_filter):
        event = CreateCallFilterEvent(call_filter.id)
        headers = self._build_headers(call_filter)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, call_filter):
        event = EditCallFilterEvent(call_filter.id)
        headers = self._build_headers(call_filter)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, call_filter):
        event = DeleteCallFilterEvent(call_filter.id)
        headers = self._build_headers(call_filter)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, call_filter):
        return {'tenant_uuid': str(call_filter.tenant_uuid)}


def build_notifier():
    return CallFilterNotifier(bus)
