# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.switchboard.event import EditSwitchboardFallbackEvent

from wazo_confd import bus

from .schema import SwitchboardFallbackSchema


class SwitchboardFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, switchboard):
        event_body = SwitchboardFallbackSchema().dump(switchboard)
        event = EditSwitchboardFallbackEvent(event_body)
        headers = self._build_headers(switchboard)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, switchboard):
        return {'tenant_uuid': str(switchboard.tenant_uuid)}


def build_notifier():
    return SwitchboardFallbackNotifier(bus)
