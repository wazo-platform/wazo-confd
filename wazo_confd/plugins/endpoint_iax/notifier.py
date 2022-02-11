# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(iax)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, iax):
        self.send_sysconfd_handlers()
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(iax)
        event = EditIAXEndpointEvent(iax_serialized)
        headers = self._build_headers(iax)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, iax):
        self.send_sysconfd_handlers()
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(iax)
        event = DeleteIAXEndpointEvent(iax_serialized)
        headers = self._build_headers(iax)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, iax):
        return {'tenant_uuid': str(iax.tenant_uuid)}


def build_notifier():
    return IAXEndpointNotifier(sysconfd, bus)
