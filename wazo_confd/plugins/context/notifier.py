# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.context.event import (
    CreateContextEvent,
    DeleteContextEvent,
    EditContextEvent,
)

from wazo_confd import bus, sysconfd

from .schema import ContextSchema

CONTEXT_FIELDS = ['id', 'name', 'type', 'tenant_uuid']


class ContextNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = CreateContextEvent(**context_serialized)
        headers = self._build_headers(context)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = EditContextEvent(**context_serialized)
        headers = self._build_headers(context)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context)
        event = DeleteContextEvent(**context_serialized)
        headers = self._build_headers(context)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, context):
        return {'tenant_uuid': str(context.tenant_uuid)}


def build_notifier():
    return ContextNotifier(bus, sysconfd)
