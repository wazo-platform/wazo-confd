# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
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
        self.bus.send_bus_event(event)

    def edited(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = EditSipEndpointEvent(sip_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = DeleteSipEndpointEvent(sip_serialized)
        self.bus.send_bus_event(event)


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
        self.bus.send_bus_event(event)

    def edited(self, sip):
        self.send_sysconfd_handlers()
        event = EditSipEndpointTemplateEvent({})
        self.bus.send_bus_event(event)

    def deleted(self, sip):
        self.send_sysconfd_handlers()
        event = DeleteSipEndpointTemplateEvent({})
        self.bus.send_bus_event(event)


def build_endpoint_notifier():
    return SipEndpointNotifier(sysconfd, bus)


def build_template_notifier():
    return SipTemplateNotifier(sysconfd, bus)
