# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
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
from wazo_confd.plugins.endpoint_sip.schema import SipSchema

LINE_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
]

ENDPOINT_SIP_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
    'username',
]

ENDPOINT_SCCP_FIELDS = [
    'id',
    'tenant_uuid',
]

ENDPOINT_CUSTOM_FIELDS = ['id', 'tenant_uuid', 'interface']


class LineEndpointNotifier:
    def __init__(self, endpoint, bus, sysconfd):
        self.endpoint = endpoint
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        if self.endpoint == 'sip':
            sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
            event = LineEndpointSIPAssociatedEvent(
                line=line_serialized, sip=sip_serialized,
            )
        elif self.endpoint == 'sccp':
            sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
            event = LineEndpointSCCPAssociatedEvent(
                line=line_serialized, sccp=sccp_serialized,
            )
        else:
            custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
            event = LineEndpointCustomAssociatedEvent(
                line=line_serialized, custom=custom_serialized,
            )
        self.bus.send_bus_event(event)

    def dissociated(self, line, endpoint):
        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        if self.endpoint == 'sip':
            sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
            event = LineEndpointSIPDissociatedEvent(
                line=line_serialized, sip=sip_serialized,
            )
        elif self.endpoint == 'sccp':
            sccp_serialized = SccpSchema(only=ENDPOINT_SCCP_FIELDS).dump(endpoint)
            event = LineEndpointSCCPDissociatedEvent(
                line=line_serialized, sccp=sccp_serialized,
            )
        else:
            custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
            event = LineEndpointCustomDissociatedEvent(
                line=line_serialized, custom=custom_serialized,
            )
        self.bus.send_bus_event(event)


def build_notifier(endpoint):
    return LineEndpointNotifier(endpoint, bus, sysconfd)
