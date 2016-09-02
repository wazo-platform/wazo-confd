# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
                    'ipbx': ['sip reload', 'dialplan reload'],
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
