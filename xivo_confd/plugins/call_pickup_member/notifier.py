# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.call_pickup_member.event import (
    CallPickupInterceptorUsersAssociatedEvent,
    CallPickupTargetUsersAssociatedEvent,
)

from xivo_confd import bus


class CallPickupUserNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def interceptor_users_associated(self, call_pickup, users):
        user_uuids = [user.uuid for user in users]
        event = CallPickupInterceptorUsersAssociatedEvent(call_pickup.id, user_uuids)
        self.bus.send_bus_event(event)

    def target_users_associated(self, call_pickup, users):
        user_uuids = [user.uuid for user in users]
        event = CallPickupTargetUsersAssociatedEvent(call_pickup.id, user_uuids)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallPickupUserNotifier(bus)
