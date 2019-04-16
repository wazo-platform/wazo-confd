# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.trunk.event import (
    CreateTrunkEvent,
    DeleteTrunkEvent,
    EditTrunkEvent,
)

from xivo_confd import bus, sysconfd


class TrunkNotifier(object):

    _IPBX_COMMANDS = {
        'sip': ['module reload res_pjsip.so'],
        'iax': ['iax2 reload'],
    }

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx_commands):
        handlers = {
            'ipbx': ipbx_commands,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, trunk):
        event = CreateTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)

    def edited(self, trunk):
        if trunk.endpoint in self._IPBX_COMMANDS:
            self.send_sysconfd_handlers(self._IPBX_COMMANDS[trunk.endpoint])
        event = EditTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)

    def deleted(self, trunk):
        if trunk.endpoint in self._IPBX_COMMANDS:
            self.send_sysconfd_handlers(self._IPBX_COMMANDS[trunk.endpoint])
        event = DeleteTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return TrunkNotifier(bus, sysconfd)
