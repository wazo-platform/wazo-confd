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
        event = QueueScheduleAssociatedEvent(queue.id, schedule.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, queue, schedule):
        event = QueueScheduleDissociatedEvent(queue.id, schedule.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, queue):
        return {'tenant_uuid': str(queue.tenant_uuid)}


def build_notifier():
    return QueueScheduleNotifier(bus)
