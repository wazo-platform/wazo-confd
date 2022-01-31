# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.schedule.event import (
    CreateScheduleEvent,
    DeleteScheduleEvent,
    EditScheduleEvent,
)

from wazo_confd import bus


class ScheduleNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, schedule):
        event = CreateScheduleEvent(schedule.id)
        headers = self._build_headers(schedule)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, schedule):
        event = EditScheduleEvent(schedule.id)
        headers = self._build_headers(schedule)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, schedule):
        event = DeleteScheduleEvent(schedule.id)
        headers = self._build_headers(schedule)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, schedule):
        return {'tenant_uuid': str(schedule.tenant_uuid)}


def build_notifier():
    return ScheduleNotifier(bus)
