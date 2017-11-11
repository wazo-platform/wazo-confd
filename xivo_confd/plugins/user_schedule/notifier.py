# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_schedule.event import (UserScheduleAssociatedEvent,
                                                      UserScheduleDissociatedEvent)


class UserScheduleNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, schedule):
        event = UserScheduleAssociatedEvent(user.id, schedule.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, user, schedule):
        event = UserScheduleDissociatedEvent(user.id, schedule.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserScheduleNotifier(bus)
