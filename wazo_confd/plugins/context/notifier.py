# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.context.event import (
    ContextCreatedEvent,
    ContextDeletedEvent,
    ContextEditedEvent,
)

from wazo_confd import bus, sysconfd

from .schema import ContextSchema

CONTEXT_FIELDS = ['id', 'name', 'type', 'tenant_uuid']


class ContextNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, context):
        self.send_sysconfd_handlers()
        context_payload = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = ContextCreatedEvent(context_payload, context.tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, context):
        self.send_sysconfd_handlers()
        context_payload = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = ContextEditedEvent(context_payload, context.tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, context):
        self.send_sysconfd_handlers()
        context_payload = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = ContextDeletedEvent(context_payload, context.tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return ContextNotifier(bus, sysconfd)
