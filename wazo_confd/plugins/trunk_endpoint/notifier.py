# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.trunk_endpoint.event import (
    TrunkEndpointCustomAssociatedEvent,
    TrunkEndpointCustomDissociatedEvent,
    TrunkEndpointIAXAssociatedEvent,
    TrunkEndpointIAXDissociatedEvent,
    TrunkEndpointSIPAssociatedEvent,
    TrunkEndpointSIPDissociatedEvent,
)

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.trunk.schema import TrunkSchema
from wazo_confd.plugins.endpoint_custom.schema import CustomSchema
from wazo_confd.plugins.endpoint_iax.schema import IAXSchema
from wazo_confd.plugins.endpoint_sip.schema import SipSchema

TRUNK_FIELDS = [
    'id',
    'tenant_uuid',
]

ENDPOINT_SIP_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
    'username',
]

ENDPOINT_IAX_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
]

ENDPOINT_CUSTOM_FIELDS = ['id', 'tenant_uuid', 'interface']


class TrunkEndpointNotifier:
    def __init__(self, endpoint, bus, sysconfd):
        self.endpoint = endpoint
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, trunk, endpoint):
        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers(['module reload res_pjsip.so'])
            sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
            event = TrunkEndpointSIPAssociatedEvent(
                trunk=trunk_serialized, sip=sip_serialized,
            )
        elif self.endpoint == 'iax':
            self.send_sysconfd_handlers(['iax2 reload'])
            iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(endpoint)
            event = TrunkEndpointIAXAssociatedEvent(
                trunk=trunk_serialized, iax=iax_serialized,
            )
        else:
            custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
            event = TrunkEndpointCustomAssociatedEvent(
                trunk=trunk_serialized, custom=custom_serialized,
            )
        self.bus.send_bus_event(event)

    def dissociated(self, trunk, endpoint):
        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers(['module reload res_pjsip.so'])
            sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
            event = TrunkEndpointSIPDissociatedEvent(
                trunk=trunk_serialized, sip=sip_serialized,
            )
        elif self.endpoint == 'iax':
            self.send_sysconfd_handlers(['iax2 reload'])
            iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(endpoint)
            event = TrunkEndpointIAXDissociatedEvent(
                trunk=trunk_serialized, iax=iax_serialized,
            )
        else:
            custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
            event = TrunkEndpointCustomDissociatedEvent(
                trunk=trunk_serialized, custom=custom_serialized,
            )
        self.bus.send_bus_event(event)


def build_notifier(endpoint):
    return TrunkEndpointNotifier(endpoint, bus, sysconfd)
