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
        event = UserScheduleAssociatedEvent(user.id, schedule.id)
        headers = self._build_headers(user)
        self._bus.send_bus_event(event, headers=headers)

    def dissociated(self, user, schedule):
        event = UserScheduleDissociatedEvent(user.id, schedule.id)
        headers = self._build_headers(user)
        self._bus.send_bus_event(event, headers=headers)

    def _build_headers(self, user):
        return {'tenant_uuid': str(user.tenant_uuid)}


def build_notifier():
    return UserScheduleNotifier(bus)
