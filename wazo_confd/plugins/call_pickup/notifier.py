# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_pickup.event import (
    CreateCallPickupEvent,
    DeleteCallPickupEvent,
    EditCallPickupEvent,
)

from wazo_confd import bus, sysconfd


class CallPickupNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, call_pickup):
        event = CreateCallPickupEvent(call_pickup.id)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, call_pickup):
        event = EditCallPickupEvent(call_pickup.id)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, call_pickup):
        self.send_sysconfd_handlers()
        event = DeleteCallPickupEvent(call_pickup.id)
        headers = self._build_headers(call_pickup)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, call_pickup):
        return {'tenant_uuid': str(call_pickup.tenant_uuid)}


def build_notifier():
    return CallPickupNotifier(bus, sysconfd)
