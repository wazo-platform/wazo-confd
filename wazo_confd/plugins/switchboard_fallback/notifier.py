# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.common.event import ArbitraryEvent

from wazo_confd import bus

from .schema import SwitchboardFallbackSchema


class SwitchboardFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, switchboard):
        event = ArbitraryEvent(
            name='switchboard_fallback_edited',
            body=SwitchboardFallbackSchema().dump(switchboard),
            required_acl='switchboards.fallbacks.edited',
        )
        event.routing_key = 'config.switchboards.fallbacks.edited'
        self.bus.send_bus_event(event)


def build_notifier():
    return SwitchboardFallbackNotifier(bus)
