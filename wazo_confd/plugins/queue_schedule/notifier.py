# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue_schedule.event import (
    QueueScheduleAssociatedEvent,
    QueueScheduleDissociatedEvent,
)

from wazo_confd import bus


class QueueScheduleNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, queue, schedule):
        event = QueueScheduleAssociatedEvent(queue.id, schedule.id, queue.tenant_uuid)
        self.bus.queue_event(event)

    def dissociated(self, queue, schedule):
        event = QueueScheduleDissociatedEvent(queue.id, schedule.id, queue.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return QueueScheduleNotifier(bus)
