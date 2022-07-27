# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall_call_permission.event import (
    OutcallCallPermissionAssociatedEvent,
    OutcallCallPermissionDissociatedEvent,
)

from wazo_confd import bus


class OutcallCallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, outcall, call_permission):
        event = OutcallCallPermissionAssociatedEvent(
            outcall.id, call_permission.id, outcall.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, outcall, call_permission):
        event = OutcallCallPermissionDissociatedEvent(
            outcall.id, call_permission.id, outcall.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return OutcallCallPermissionNotifier(bus)
