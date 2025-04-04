# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.line_endpoint.event import (
    LineEndpointCustomAssociatedEvent,
    LineEndpointCustomDissociatedEvent,
    LineEndpointSCCPAssociatedEvent,
    LineEndpointSCCPDissociatedEvent,
    LineEndpointSIPAssociatedEvent,
    LineEndpointSIPDissociatedEvent,
)

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.endpoint_custom.schema import CustomSchema
from wazo_confd.plugins.endpoint_sccp.schema import SccpSchema
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema
from wazo_confd.plugins.line.schema import LineSchema

LINE_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
]

ENDPOINT_SIP_FIELDS = [
    'uuid',
    'tenant_uuid',
    'label',
    'name',
    'auth_section_options.username',
]

ENDPOINT_SCCP_FIELDS = [
    'id',
    'tenant_uuid',
]

ENDPOINT_CUSTOM_FIELDS = ['id', 'tenant_uuid', 'interface']


class LineEndpointSIPNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload res_pjsip.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, endpoint):
        self.send_sysconfd_handlers()
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = LineEndpointSIPAssociatedEvent(
            line_serialized, sip_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, line, endpoint):
        self.send_sysconfd_handlers()
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = LineEndpointSIPDissociatedEvent(
            line_serialized, sip_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)


class LineEndpointSCCPNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload chan_sccp.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, endpoint):
        self.send_sysconfd_handlers()
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
        event = LineEndpointSCCPAssociatedEvent(
            line_serialized, sccp_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, line, endpoint):
        self.send_sysconfd_handlers()
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
        event = LineEndpointSCCPDissociatedEvent(
            line_serialized, sccp_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)


class LineEndpointCustomNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = LineEndpointCustomAssociatedEvent(
            line_serialized, custom_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = LineEndpointCustomDissociatedEvent(
            line_serialized, custom_serialized, line.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier_sip():
    return LineEndpointSIPNotifier(bus, sysconfd)


def build_notifier_sccp():
    return LineEndpointSCCPNotifier(bus, sysconfd)


def build_notifier_custom():
    return LineEndpointCustomNotifier(bus)
