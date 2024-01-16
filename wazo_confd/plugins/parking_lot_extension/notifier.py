# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.parking_lot_extension.event import (
    ParkingLotExtensionAssociatedEvent,
    ParkingLotExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class ParkingLotExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload res_parking.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionAssociatedEvent(
            parking_lot.id, extension.id, parking_lot.tenant_uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionDissociatedEvent(
            parking_lot.id, extension.id, parking_lot.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return ParkingLotExtensionNotifier(bus, sysconfd)
