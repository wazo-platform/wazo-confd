# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.incall.event import (
    CreateIncallEvent,
    DeleteIncallEvent,
    EditIncallEvent,
)

from wazo_confd import bus


class IncallNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, incall):
        event = CreateIncallEvent(incall.id)
        headers = self._build_headers(incall)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, incall):
        event = EditIncallEvent(incall.id)
        headers = self._build_headers(incall)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, incall):
        event = DeleteIncallEvent(incall.id)
        headers = self._build_headers(incall)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, incall):
        return {'tenant_uuid': str(incall.tenant_uuid)}


def build_notifier():
    return IncallNotifier(bus)
