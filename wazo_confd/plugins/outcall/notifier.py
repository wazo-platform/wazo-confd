# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall.event import (
    CreateOutcallEvent,
    DeleteOutcallEvent,
    EditOutcallEvent,
)

from wazo_confd import bus


class OutcallNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, outcall):
        event = CreateOutcallEvent(outcall.id)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, outcall):
        event = EditOutcallEvent(outcall.id)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, outcall):
        event = DeleteOutcallEvent(outcall.id)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, outcall):
        return {'tenant_uuid': str(outcall.tenant_uuid)}


def build_notifier():
    return OutcallNotifier(bus)
