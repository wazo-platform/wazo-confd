# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall_extension.event import (
    OutcallExtensionAssociatedEvent,
    OutcallExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class OutcallExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, outcall, extension):
        self.send_sysconfd_handlers()
        event = OutcallExtensionAssociatedEvent(outcall.id, extension.id)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, outcall, extension):
        self.send_sysconfd_handlers()
        event = OutcallExtensionDissociatedEvent(outcall.id, extension.id)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, outcall):
        return {'tenant_uuid': str(outcall.tenant_uuid)}


def build_notifier():
    return OutcallExtensionNotifier(bus, sysconfd)
