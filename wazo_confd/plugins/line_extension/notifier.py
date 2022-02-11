# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.line_extension.event import (
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
            ],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, extension):
        self.send_sysconfd_handlers()
        event = LineExtensionAssociatedEvent(line.id, extension.id)
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, line, extension):
        self.send_sysconfd_handlers()
        event = LineExtensionDissociatedEvent(line.id, extension.id)
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, line):
        return {'tenant_uuid': str(line.tenant_uuid)}


def build_notifier():
    return LineExtensionNotifier(bus, sysconfd)
