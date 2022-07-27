# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.incall_extension.event import (
    IncallExtensionAssociatedEvent,
    IncallExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class IncallExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, incall, extension):
        self.send_sysconfd_handlers()
        event = IncallExtensionAssociatedEvent(incall.id, extension.id)
        headers = self._build_headers(incall)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, incall, extension):
        self.send_sysconfd_handlers()
        event = IncallExtensionDissociatedEvent(incall.id, extension.id)
        headers = self._build_headers(incall)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, incall):
        return {'tenant_uuid': str(incall.tenant_uuid)}


def build_notifier():
    return IncallExtensionNotifier(bus, sysconfd)
