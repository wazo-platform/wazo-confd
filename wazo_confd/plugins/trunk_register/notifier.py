# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.trunk_register.event import (
    TrunkRegisterIAXAssociatedEvent,
    TrunkRegisterIAXDissociatedEvent,
)

from wazo_confd import bus


class TrunkRegisterIAXNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, trunk, register):
        event = TrunkRegisterIAXAssociatedEvent(trunk.id, register.id)
        headers = self._build_headers(trunk)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, trunk, register):
        event = TrunkRegisterIAXDissociatedEvent(trunk.id, register.id)
        headers = self._build_headers(trunk)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, trunk):
        return {'tenant_uuid': str(trunk.tenant_uuid)}


def build_notifier_iax():
    return TrunkRegisterIAXNotifier(bus)
