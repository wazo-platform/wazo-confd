# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_schedule.event import (
    UserScheduleAssociatedEvent,
    UserScheduleDissociatedEvent,
)

from xivo_confd import bus


class UserScheduleNotifier(object):

    def __init__(self, bus):
        self._bus = bus

    def associated(self, user, schedule):
        event = UserScheduleAssociatedEvent(user.id, schedule.id)
        self._bus.send_bus_event(event)

    def dissociated(self, user, schedule):
        event = UserScheduleDissociatedEvent(user.id, schedule.id)
        self._bus.send_bus_event(event)


def build_notifier():
    return UserScheduleNotifier(bus)
