# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.parking_lot_extension.event import (
    ParkingLotExtensionAssociatedEvent,
    ParkingLotExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class ParkingLotExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload res_parking.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionAssociatedEvent(parking_lot.id, extension.id)
        headers = self._build_headers(parking_lot)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionDissociatedEvent(parking_lot.id, extension.id)
        headers = self._build_headers(parking_lot)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, parking_lot):
        return {'tenant_uuid': str(parking_lot.tenant_uuid)}


def build_notifier():
    return ParkingLotExtensionNotifier(bus, sysconfd)
