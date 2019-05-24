# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.schedule.event import (
    CreateScheduleEvent,
    DeleteScheduleEvent,
    EditScheduleEvent,
)

from xivo_confd import bus


class ScheduleNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, schedule):
        event = CreateScheduleEvent(schedule.id)
        self.bus.send_bus_event(event)

    def edited(self, schedule):
        event = EditScheduleEvent(schedule.id)
        self.bus.send_bus_event(event)

    def deleted(self, schedule):
        event = DeleteScheduleEvent(schedule.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return ScheduleNotifier(bus)
