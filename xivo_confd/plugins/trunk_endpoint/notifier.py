# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd
from xivo_bus.resources.trunk_endpoint.event import (TrunkEndpointAssociatedEvent,
                                                     TrunkEndpointDissociatedEvent)


class TrunkEndpointNotifier(object):

    def __init__(self, endpoint, bus, sysconfd):
        self.endpoint = endpoint
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['sip reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, trunk, endpoint):
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers()
        event = TrunkEndpointAssociatedEvent(trunk.id, endpoint.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, trunk, endpoint):
        if self.endpoint == 'sip':
            self.send_sysconfd_handlers()
        event = TrunkEndpointDissociatedEvent(trunk.id, endpoint.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier(endpoint):
    return TrunkEndpointNotifier(endpoint, bus, sysconfd)
