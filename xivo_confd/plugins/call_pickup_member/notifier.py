# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_pickup_member.event import (
    CallPickupInterceptorGroupsAssociatedEvent,
    CallPickupInterceptorUsersAssociatedEvent,
    CallPickupTargetGroupsAssociatedEvent,
    CallPickupTargetUsersAssociatedEvent,
)

from xivo_confd import bus, sysconfd


class CallPickupMemberNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ctibus': [],
            'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def interceptor_groups_associated(self, call_pickup, groups):
        self.send_sysconfd_handlers()
        group_ids = [group.id for group in groups]
        event = CallPickupInterceptorGroupsAssociatedEvent(call_pickup.id, group_ids)
        self.bus.send_bus_event(event)

    def target_groups_associated(self, call_pickup, groups):
        self.send_sysconfd_handlers()
        group_ids = [group.id for group in groups]
        event = CallPickupTargetGroupsAssociatedEvent(call_pickup.id, group_ids)
        self.bus.send_bus_event(event)

    def interceptor_users_associated(self, call_pickup, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = CallPickupInterceptorUsersAssociatedEvent(call_pickup.id, user_uuids)
        self.bus.send_bus_event(event)

    def target_users_associated(self, call_pickup, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = CallPickupTargetUsersAssociatedEvent(call_pickup.id, user_uuids)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallPickupMemberNotifier(bus, sysconfd)
