# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.conference_extension.event import (
    ConferenceExtensionAssociatedEvent,
    ConferenceExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class ConferenceExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, conference, extension):
        self.send_sysconfd_handlers()
        event = ConferenceExtensionAssociatedEvent(
            conference.id, extension.id, conference.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, conference, extension):
        self.send_sysconfd_handlers()
        event = ConferenceExtensionDissociatedEvent(
            conference.id, extension.id, conference.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return ConferenceExtensionNotifier(bus, sysconfd)
