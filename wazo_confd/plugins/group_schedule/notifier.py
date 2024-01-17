# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.group_schedule.event import (
    GroupScheduleAssociatedEvent,
    GroupScheduleDissociatedEvent,
)

from wazo_confd import bus


class GroupScheduleNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, group, schedule):
        event = GroupScheduleAssociatedEvent(
            group.id, group.uuid, schedule.id, group.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, group, schedule):
        event = GroupScheduleDissociatedEvent(
            group.id, group.uuid, schedule.id, group.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return GroupScheduleNotifier(bus)
