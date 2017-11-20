# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent


class UserEntityNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, entity):
        event = UserEntityAssociatedEvent(user.uuid, entity.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserEntityNotifier(bus)
