# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue.event import (
    CreateQueueEvent,
    EditQueueEvent,
    DeleteQueueEvent,
)

from wazo_confd import bus, sysconfd


class QueueNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, queue):
        self.send_sysconfd_handlers()
        event = CreateQueueEvent(queue.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, queue):
        self.send_sysconfd_handlers()
        event = EditQueueEvent(queue.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, queue):
        self.send_sysconfd_handlers()
        event = DeleteQueueEvent(queue.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, queue):
        return {'tenant_uuid': str(queue.tenant_uuid)}


def build_notifier():
    return QueueNotifier(bus, sysconfd)
