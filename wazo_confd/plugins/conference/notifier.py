# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.conference.event import (
    CreateConferenceEvent,
    DeleteConferenceEvent,
    EditConferenceEvent,
)

from wazo_confd import bus, sysconfd


class ConferenceNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_confbridge.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, conference):
        self.send_sysconfd_handlers()
        event = CreateConferenceEvent(conference.id)
        headers = self._build_headers(conference)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, conference):
        self.send_sysconfd_handlers()
        event = EditConferenceEvent(conference.id)
        headers = self._build_headers(conference)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, conference):
        self.send_sysconfd_handlers()
        event = DeleteConferenceEvent(conference.id)
        headers = self._build_headers(conference)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, conference):
        return {'tenant_uuid': str(conference.tenant_uuid)}


def build_notifier():
    return ConferenceNotifier(bus, sysconfd)
