# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.group_call_permission.event import (
    GroupCallPermissionAssociatedEvent,
    GroupCallPermissionDissociatedEvent,
)

from wazo_confd import bus


class GroupCallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, call_permission):
        event = GroupCallPermissionAssociatedEvent(
            group.id, group.uuid, call_permission.id, group.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, group, call_permission):
        event = GroupCallPermissionDissociatedEvent(
            group.id, group.uuid, call_permission.id, group.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return GroupCallPermissionNotifier(bus)
