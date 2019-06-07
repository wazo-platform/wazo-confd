# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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
        handlers = {
            'ipbx': ['module reload app_queue.so'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, queue):
        self.send_sysconfd_handlers()
        event = CreateQueueEvent(queue.id)
        self.bus.send_bus_event(event)

    def edited(self, queue):
        self.send_sysconfd_handlers()
        event = EditQueueEvent(queue.id)
        self.bus.send_bus_event(event)

    def deleted(self, queue):
        self.send_sysconfd_handlers()
        event = DeleteQueueEvent(queue.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return QueueNotifier(bus, sysconfd)
