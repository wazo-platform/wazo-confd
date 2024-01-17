# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.conference.event import (
    ConferenceCreatedEvent,
    ConferenceDeletedEvent,
    ConferenceEditedEvent,
)

from wazo_confd import bus, sysconfd


class ConferenceNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_confbridge.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, conference):
        self.send_sysconfd_handlers()
        event = ConferenceCreatedEvent(conference.id, conference.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, conference):
        self.send_sysconfd_handlers()
        event = ConferenceEditedEvent(conference.id, conference.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, conference):
        self.send_sysconfd_handlers()
        event = ConferenceDeletedEvent(conference.id, conference.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return ConferenceNotifier(bus, sysconfd)
