# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_schedule.event import (
    GroupScheduleAssociatedEvent,
    GroupScheduleDissociatedEvent,
)

from wazo_confd import bus


class GroupScheduleNotifier:

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
