# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.trunk.event import (CreateTrunkEvent,
                                            EditTrunkEvent,
                                            DeleteTrunkEvent)


class TrunkNotifier(object):

    _IPBX_COMMANDS = {
        'sip': ['sip reload'],
        'iax': ['iax2 reload'],
    }

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx_commands):
        handlers = {'ctibus': [],
                    'ipbx': ipbx_commands,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, trunk):
        event = CreateTrunkEvent(trunk.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, trunk):
        if trunk.endpoint in self._IPBX_COMMANDS:
            self.send_sysconfd_handlers(self._IPBX_COMMANDS[trunk.endpoint])
        event = EditTrunkEvent(trunk.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, trunk):
        if trunk.endpoint in self._IPBX_COMMANDS:
            self.send_sysconfd_handlers(self._IPBX_COMMANDS[trunk.endpoint])
        event = DeleteTrunkEvent(trunk.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return TrunkNotifier(bus, sysconfd)
