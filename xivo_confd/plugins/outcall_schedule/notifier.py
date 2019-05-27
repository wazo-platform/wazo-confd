# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall_schedule.event import (
    OutcallScheduleAssociatedEvent,
    OutcallScheduleDissociatedEvent,
)

from xivo_confd import bus


class OutcallScheduleNotifier:

    def __init__(self, bus):
        self._bus = bus

    def associated(self, outcall, schedule):
        event = OutcallScheduleAssociatedEvent(outcall.id, schedule.id)
        self._bus.send_bus_event(event)

    def dissociated(self, outcall, schedule):
        event = OutcallScheduleDissociatedEvent(outcall.id, schedule.id)
        self._bus.send_bus_event(event)


def build_notifier():
    return OutcallScheduleNotifier(bus)
