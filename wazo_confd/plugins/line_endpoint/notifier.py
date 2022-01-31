# Copyright 2019-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.line_endpoint.event import (
    LineEndpointCustomAssociatedEvent,
    LineEndpointCustomDissociatedEvent,
    LineEndpointSCCPAssociatedEvent,
    LineEndpointSCCPDissociatedEvent,
    LineEndpointSIPAssociatedEvent,
    LineEndpointSIPDissociatedEvent,
)

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.line.schema import LineSchema
from wazo_confd.plugins.endpoint_custom.schema import CustomSchema
from wazo_confd.plugins.endpoint_sccp.schema import SccpSchema
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema

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

    def associated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = LineEndpointSIPAssociatedEvent(
            line=line_serialized,
            sip=sip_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = LineEndpointSIPDissociatedEvent(
            line=line_serialized,
            sip=sip_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, line):
        return {'tenant_uuid': str(line.tenant_uuid)}


class LineEndpointSCCPNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def associated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
        event = LineEndpointSCCPAssociatedEvent(
            line=line_serialized,
            sccp=sccp_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
        event = LineEndpointSCCPDissociatedEvent(
            line=line_serialized,
            sccp=sccp_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, line):
        return {'tenant_uuid': str(line.tenant_uuid)}


class LineEndpointCustomNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def associated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = LineEndpointCustomAssociatedEvent(
            line=line_serialized,
            custom=custom_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = LineEndpointCustomDissociatedEvent(
            line=line_serialized,
            custom=custom_serialized,
        )
        headers = self._build_headers(line)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, line):
        return {'tenant_uuid': str(line.tenant_uuid)}


def build_notifier_sip():
    return LineEndpointSIPNotifier(bus, sysconfd)


def build_notifier_sccp():
    return LineEndpointSCCPNotifier(bus, sysconfd)


def build_notifier_custom():
    return LineEndpointCustomNotifier(bus, sysconfd)
