# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_call_permission.event import (
    GroupCallPermissionAssociatedEvent,
    GroupCallPermissionDissociatedEvent,
)

from xivo_confd import bus


class GroupCallPermissionNotifier:

    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, call_permission):
        event = GroupCallPermissionAssociatedEvent(group.id, call_permission.id)
        self.bus.send_bus_event(event)

    def dissociated(self, group, call_permission):
        event = GroupCallPermissionDissociatedEvent(group.id, call_permission.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupCallPermissionNotifier(bus)
