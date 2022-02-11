# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, queue, extension):
        self.send_sysconfd_handlers()
        event = QueueExtensionDissociatedEvent(queue.id, extension.id)
        headers = self._build_headers(queue)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, queue):
        return {'tenant_uuid': str(queue.tenant_uuid)}


def build_notifier():
    return QueueExtensionNotifier(bus, sysconfd)
