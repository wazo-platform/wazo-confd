# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_sip.event import (
    CreateSipEndpointEvent,
    DeleteSipEndpointEvent,
    EditSipEndpointEvent,
)

from wazo_confd import bus, sysconfd

from .schema import SipSchema

ENDPOINT_SIP_FIELDS = [
    'id',
    'tenant_uuid',
    'name',
    'username',
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
        sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = CreateSipEndpointEvent(sip_serialized)
        self.bus.send_bus_event(event)

    def edited(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = EditSipEndpointEvent(sip_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, sip):
        self.send_sysconfd_handlers()
        sip_serialized = SipSchema(only=ENDPOINT_SIP_FIELDS).dump(sip)
        event = DeleteSipEndpointEvent(sip_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return SipEndpointNotifier(sysconfd, bus)
