# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.trunk_register.event import (
    TrunkRegisterIAXAssociatedEvent,
    TrunkRegisterIAXDissociatedEvent,
)

from wazo_confd import bus


class TrunkRegisterIAXNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, trunk, register):
        event = TrunkRegisterIAXAssociatedEvent(
            trunk.id, register.id, trunk.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, trunk, register):
        event = TrunkRegisterIAXDissociatedEvent(
            trunk.id, register.id, trunk.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier_iax():
    return TrunkRegisterIAXNotifier(bus)
