# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.queue.event import QueueFallbackEditedEvent

from wazo_confd import bus


class QueueFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, queue):
        event = QueueFallbackEditedEvent(queue.id, queue.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return QueueFallbackNotifier(bus)
