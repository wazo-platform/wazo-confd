# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.ivr.event import CreateIvrEvent, DeleteIvrEvent, EditIvrEvent

from wazo_confd import bus, sysconfd


class IvrNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, ivr):
        self.send_sysconfd_handlers()
        event = CreateIvrEvent(ivr.id)
        headers = self._build_headers(ivr)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, ivr):
        self.send_sysconfd_handlers()
        event = EditIvrEvent(ivr.id)
        headers = self._build_headers(ivr)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, ivr):
        self.send_sysconfd_handlers()
        event = DeleteIvrEvent(ivr.id)
        headers = self._build_headers(ivr)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, ivr):
        return {'tenant_uuid': str(ivr.tenant_uuid)}


def build_notifier():
    return IvrNotifier(bus, sysconfd)
