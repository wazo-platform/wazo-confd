# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.line_extension.event import (
    LineExtensionAssociatedEvent,
    LineExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class LineExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': [
                'dialplan reload',
                'module reload res_pjsip.so',
                'module reload app_queue.so',
            ]
        }
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, extension):
        self.send_sysconfd_handlers()
        event = LineExtensionAssociatedEvent(line.id, extension.id, line.tenant_uuid)
        self.bus.queue_event(event)

    def dissociated(self, line, extension):
        self.send_sysconfd_handlers()
        event = LineExtensionDissociatedEvent(line.id, extension.id, line.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return LineExtensionNotifier(bus, sysconfd)
