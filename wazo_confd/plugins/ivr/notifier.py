# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.ivr.event import (
    IVRCreatedEvent,
    IVRDeletedEvent,
    IVREditedEvent,
)

from wazo_confd import bus, sysconfd


class IvrNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, ivr):
        self.send_sysconfd_handlers()
        event = IVRCreatedEvent(ivr.id, ivr.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, ivr):
        self.send_sysconfd_handlers()
        event = IVREditedEvent(ivr.id, ivr.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, ivr):
        self.send_sysconfd_handlers()
        event = IVRDeletedEvent(ivr.id, ivr.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return IvrNotifier(bus, sysconfd)
