# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

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
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema

logger = logging.getLogger(__name__)

TRUNK_FIELDS = [
    'id',
    'tenant_uuid',
]

ENDPOINT_SIP_FIELDS = [
    'uuid',
    'tenant_uuid',
    'name',
    'auth_section_options.username',
]

ENDPOINT_IAX_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
]

ENDPOINT_CUSTOM_FIELDS = ['id', 'tenant_uuid', 'interface']


class TrunkEndpointNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)


class TrunkEndpointSIPNotifier(TrunkEndpointNotifier):
    def associated(self, trunk, endpoint):
        self.send_sysconfd_handlers(['module reload res_pjsip.so'])

        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = TrunkEndpointSIPAssociatedEvent(
            trunk=trunk_serialized,
            sip=sip_serialized,
        )
        self.bus.send_bus_event(event)

    def dissociated(self, trunk, endpoint):
        self.send_sysconfd_handlers(['module reload res_pjsip.so'])

        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        sip_serialized = EndpointSIPSchema(only=ENDPOINT_SIP_FIELDS).dump(endpoint)
        event = TrunkEndpointSIPDissociatedEvent(
            trunk=trunk_serialized,
            sip=sip_serialized,
        )
        self.bus.send_bus_event(event)


class TrunkEndpointIAXNotifier(TrunkEndpointNotifier):
    def associated(self, trunk, endpoint):
        self.send_sysconfd_handlers(['iax2 reload'])

        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(endpoint)
        event = TrunkEndpointIAXAssociatedEvent(
            trunk=trunk_serialized,
            iax=iax_serialized,
        )
        self.bus.send_bus_event(event)

    def dissociated(self, trunk, endpoint):
        self.send_sysconfd_handlers(['iax2 reload'])

        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        iax_serialized = IAXSchema(only=ENDPOINT_IAX_FIELDS).dump(endpoint)
        event = TrunkEndpointIAXDissociatedEvent(
            trunk=trunk_serialized,
            iax=iax_serialized,
        )
        self.bus.send_bus_event(event)


class TrunkEndpointCustomNotifier(TrunkEndpointNotifier):
    def associated(self, trunk, endpoint):
        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = TrunkEndpointCustomAssociatedEvent(
            trunk=trunk_serialized,
            custom=custom_serialized,
        )
        self.bus.send_bus_event(event)

    def dissociated(self, trunk, endpoint):
        trunk_serialized = TrunkSchema(only=TRUNK_FIELDS).dump(trunk)
        custom_serialized = CustomSchema(only=ENDPOINT_CUSTOM_FIELDS).dump(endpoint)
        event = TrunkEndpointCustomDissociatedEvent(
            trunk=trunk_serialized,
            custom=custom_serialized,
        )
        self.bus.send_bus_event(event)


def build_notifier_sip():
    return TrunkEndpointSIPNotifier(bus, sysconfd)


def build_notifier_iax():
    return TrunkEndpointIAXNotifier(bus, sysconfd)


def build_notifier_custom():
    return TrunkEndpointCustomNotifier(bus, sysconfd)
