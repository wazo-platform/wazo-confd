# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
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
        handlers = {'ipbx': ipbx_commands}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, trunk):
        event = CreateTrunkEvent(trunk.id)
        headers = self._build_headers(trunk)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, trunk):
        if trunk.endpoint_sip_uuid:
            self.send_sysconfd_handlers(self._SIP_IPBX_COMMANDS)
        if trunk.endpoint_iax_id:
            self.send_sysconfd_handlers(self._IAX_IPBX_COMMANDS)
        event = EditTrunkEvent(trunk.id)
        headers = self._build_headers(trunk)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, trunk):
        if trunk.endpoint_sip_uuid:
            self.send_sysconfd_handlers(self._SIP_IPBX_COMMANDS)
        if trunk.endpoint_iax_id:
            self.send_sysconfd_handlers(self._IAX_IPBX_COMMANDS)
        event = DeleteTrunkEvent(trunk.id)
        headers = self._build_headers(trunk)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, trunk):
        return {'tenant_uuid': str(trunk.tenant_uuid)}


def build_notifier():
    return TrunkNotifier(bus, sysconfd)
