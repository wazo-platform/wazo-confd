# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_iax.event import (
    CreateIAXEndpointEvent,
    DeleteIAXEndpointEvent,
    EditIAXEndpointEvent,
)

from wazo_confd import bus, sysconfd

from .schema import IAXSchema

ENDPOINT_IAX_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
    'trunk.id',
]


class IAXEndpointNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['iax2 reload'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, iax):
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(iax)
        event = CreateIAXEndpointEvent(iax_serialized)
        self.bus.send_bus_event(event)

    def edited(self, iax):
        self.send_sysconfd_handlers()
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(iax)
        event = EditIAXEndpointEvent(iax_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, iax):
        self.send_sysconfd_handlers()
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(iax)
        event = DeleteIAXEndpointEvent(iax_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return IAXEndpointNotifier(sysconfd, bus)
