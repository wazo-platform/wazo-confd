# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_call_permission.event import (
    GroupCallPermissionAssociatedEvent,
    GroupCallPermissionDissociatedEvent,
)

from wazo_confd import bus


class GroupCallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, call_permission):
        event = GroupCallPermissionAssociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            call_permission_id=call_permission.id,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, group, call_permission):
        event = GroupCallPermissionDissociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            call_permission_id=call_permission.id,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, group):
        return {'tenant_uuid': str(group.tenant_uuid)}


def build_notifier():
    return GroupCallPermissionNotifier(bus)
