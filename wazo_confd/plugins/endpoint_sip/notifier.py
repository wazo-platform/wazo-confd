# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_sip.event import (
    CreateSipEndpointEvent,
    CreateSipEndpointTemplateEvent,
    DeleteSipEndpointEvent,
    DeleteSipEndpointTemplateEvent,
    EditSipEndpointEvent,
    EditSipEndpointTemplateEvent,
)

from wazo_confd import bus, sysconfd

from .schema import EndpointSIPSchema

ENDPOINT_SIP_FIELDS = [
    'uuid',
    'tenant_uuid',
    'name',
    'label',
    'auth_section_options.username',
    'registration_section_options.client_uri',
    'trunk.id',
    'line.id',
]


class SipEndpointNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'dialplan reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, sip):
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = CreateSipEndpointEvent(sip_serialized)
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = EditSipEndpointEvent(sip_serialized)
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = DeleteSipEndpointEvent(sip_serialized)
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, sip):
        return {'tenant_uuid': str(sip.tenant_uuid)}


class SipTemplateNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'dialplan reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, sip):
        event = CreateSipEndpointTemplateEvent({})
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, sip):
        self.send_sysconfd_handlers()
        event = EditSipEndpointTemplateEvent({})
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, sip):
        self.send_sysconfd_handlers()
        event = DeleteSipEndpointTemplateEvent({})
        headers = self._build_headers(sip)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, sip):
        return {'tenant_uuid': sip.tenant_uuid}


def build_endpoint_notifier():
    return SipEndpointNotifier(sysconfd, bus)


def build_template_notifier():
    return SipTemplateNotifier(sysconfd, bus)
