# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue_extension.event import (
    QueueExtensionAssociatedEvent,
    QueueExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class QueueExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, queue, extension):
        self.send_sysconfd_handlers()
        event = QueueExtensionAssociatedEvent(queue.id, extension.id)
        self.bus.send_bus_event(event)

    def dissociated(self, queue, extension):
        self.send_sysconfd_handlers()
        event = QueueExtensionDissociatedEvent(queue.id, extension.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return QueueExtensionNotifier(bus, sysconfd)
