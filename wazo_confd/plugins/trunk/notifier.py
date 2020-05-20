# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.trunk.event import (
    CreateTrunkEvent,
    DeleteTrunkEvent,
    EditTrunkEvent,
)

from wazo_confd import bus, sysconfd


class TrunkNotifier:

    _SIP_IPBX_COMMANDS = ['module reload res_pjsip.so']
    _IAX_IPBX_COMMANDS = ['iax2 reload']

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx_commands):
        handlers = {'ipbx': ipbx_commands, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, trunk):
        event = CreateTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)

    def edited(self, trunk):
        if trunk.endpoint_sip_id:
            self.send_sysconfd_handlers(self._SIP_IPBX_COMMANDS)
        if trunk.endpoint_iax_id:
            self.send_sysconfd_handlers(self._IAX_IPBX_COMMANDS)
        event = EditTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)

    def deleted(self, trunk):
        if trunk.endpoint_sip_id:
            self.send_sysconfd_handlers(self._SIP_IPBX_COMMANDS)
        if trunk.endpoint_iax_id:
            self.send_sysconfd_handlers(self._IAX_IPBX_COMMANDS)
        event = DeleteTrunkEvent(trunk.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return TrunkNotifier(bus, sysconfd)
