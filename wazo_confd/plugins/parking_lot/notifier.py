# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.parking_lot.event import (
    CreateParkingLotEvent,
    DeleteParkingLotEvent,
    EditParkingLotEvent,
)

from wazo_confd import bus, sysconfd


class ParkingLotNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload res_parking.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, parking_lot):
        self.send_sysconfd_handlers()
        event = CreateParkingLotEvent(parking_lot.id)
        headers = self._build_headers(parking_lot)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, parking_lot):
        self.send_sysconfd_handlers()
        event = EditParkingLotEvent(parking_lot.id)
        headers = self._build_headers(parking_lot)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, parking_lot):
        self.send_sysconfd_handlers()
        event = DeleteParkingLotEvent(parking_lot.id)
        headers = self._build_headers(parking_lot)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, parking_lot):
        return {'tenant_uuid': str(parking_lot.tenant_uuid)}


def build_notifier():
    return ParkingLotNotifier(bus, sysconfd)
