# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_pickup_member.event import (
    CallPickupInterceptorGroupsAssociatedEvent,
    CallPickupInterceptorUsersAssociatedEvent,
    CallPickupTargetGroupsAssociatedEvent,
    CallPickupTargetUsersAssociatedEvent,
)

from wazo_confd import bus, sysconfd


class CallPickupMemberNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def interceptor_groups_associated(self, call_pickup, groups):
        self.send_sysconfd_handlers()
        group_ids = [group.id for group in groups]
        event = CallPickupInterceptorGroupsAssociatedEvent(call_pickup.id, group_ids)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def target_groups_associated(self, call_pickup, groups):
        self.send_sysconfd_handlers()
        group_ids = [group.id for group in groups]
        event = CallPickupTargetGroupsAssociatedEvent(call_pickup.id, group_ids)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def interceptor_users_associated(self, call_pickup, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = CallPickupInterceptorUsersAssociatedEvent(call_pickup.id, user_uuids)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def target_users_associated(self, call_pickup, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = CallPickupTargetUsersAssociatedEvent(call_pickup.id, user_uuids)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, call_pickup):
        return {'tenant_uuid': str(call_pickup.tenant_uuid)}


def build_notifier():
    return CallPickupMemberNotifier(bus, sysconfd)
