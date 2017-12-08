# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent


class UserEntityNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, entity):
        event = UserEntityAssociatedEvent(user.uuid, entity.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserEntityNotifier(bus)
