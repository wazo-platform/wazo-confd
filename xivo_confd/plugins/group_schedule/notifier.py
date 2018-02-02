# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.group_schedule.event import (
    GroupScheduleAssociatedEvent,
    GroupScheduleDissociatedEvent,
)

from xivo_confd import bus


class GroupScheduleNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, schedule):
        event = GroupScheduleAssociatedEvent(group.id, schedule.id)
        self.bus.send_bus_event(event)

    def dissociated(self, group, schedule):
        event = GroupScheduleDissociatedEvent(group.id, schedule.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupScheduleNotifier(bus)
