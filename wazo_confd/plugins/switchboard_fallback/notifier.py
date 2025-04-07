# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.switchboard.event import SwitchboardFallbackEditedEvent

from wazo_confd import bus

from .schema import SwitchboardFallbackSchema


class SwitchboardFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, switchboard):
        payload = SwitchboardFallbackSchema().dump(switchboard)
        event = SwitchboardFallbackEditedEvent(
            payload, switchboard.uuid, switchboard.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return SwitchboardFallbackNotifier(bus)
