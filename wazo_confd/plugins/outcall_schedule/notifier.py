# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.outcall_schedule.event import (
    OutcallScheduleAssociatedEvent,
    OutcallScheduleDissociatedEvent,
)

from wazo_confd import bus


class OutcallScheduleNotifier:
    def __init__(self, bus):
        self._bus = bus

    def associated(self, outcall, schedule):
        event = OutcallScheduleAssociatedEvent(
            outcall.id, schedule.id, outcall.tenant_uuid
        )
        self._bus.queue_event(event)

    def dissociated(self, outcall, schedule):
        event = OutcallScheduleDissociatedEvent(
            outcall.id, schedule.id, outcall.tenant_uuid
        )
        self._bus.queue_event(event)


def build_notifier():
    return OutcallScheduleNotifier(bus)
