# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_schedule.event import (
    UserScheduleAssociatedEvent,
    UserScheduleDissociatedEvent,
)

from wazo_confd import bus


class UserScheduleNotifier:
    def __init__(self, bus):
        self._bus = bus

    def associated(self, user, schedule):
        event = UserScheduleAssociatedEvent(schedule.id, user.tenant_uuid, user.uuid)
        self._bus.queue_event(event)

    def dissociated(self, user, schedule):
        event = UserScheduleDissociatedEvent(schedule.id, user.tenant_uuid, user.uuid)
        self._bus.queue_event(event)


def build_notifier():
    return UserScheduleNotifier(bus)
