# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue.event import EditQueueFallbackEvent

from wazo_confd import bus


class QueueFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, queue):
        event = EditQueueFallbackEvent(queue.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, queue):
        return {'tenant_uuid': str(queue.tenant_uuid)}


def build_notifier():
    return QueueFallbackNotifier(bus)
