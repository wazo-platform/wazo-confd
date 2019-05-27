# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.trunk_endpoint.event import (
    TrunkEndpointAssociatedEvent,
    TrunkEndpointDissociatedEvent,
)

from xivo_confd import bus, sysconfd


class TrunkEndpointNotifier:

    def __init__(self, endpoint, bus, sysconfd):
        self.endpoint = endpoint
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, trunk, endpoint):
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers(['module reload res_pjsip.so'])
        elif self.endpoint == 'iax':
            self.send_sysconfd_handlers(['iax2 reload'])
        event = TrunkEndpointAssociatedEvent(trunk.id, endpoint.id)
        self.bus.send_bus_event(event)

    def dissociated(self, trunk, endpoint):
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers(['module reload res_pjsip.so'])
        elif self.endpoint == 'iax':
            self.send_sysconfd_handlers(['iax2 reload'])
        event = TrunkEndpointDissociatedEvent(trunk.id, endpoint.id)
        self.bus.send_bus_event(event)


def build_notifier(endpoint):
    return TrunkEndpointNotifier(endpoint, bus, sysconfd)
