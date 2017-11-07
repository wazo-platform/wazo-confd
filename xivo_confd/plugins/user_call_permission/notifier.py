# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_call_permission.event import (UserCallPermissionAssociatedEvent,
                                                           UserCallPermissionDissociatedEvent)


class UserCallPermissionNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, call_permission):
        event = UserCallPermissionAssociatedEvent(user.uuid, call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, user, call_permission):
        event = UserCallPermissionDissociatedEvent(user.uuid, call_permission.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserCallPermissionNotifier(bus)
