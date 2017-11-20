# -*- coding: utf-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd
from xivo_bus.resources.parking_lot_extension.event import (ParkingLotExtensionAssociatedEvent,
                                                            ParkingLotExtensionDissociatedEvent)


class ParkingLotExtensionNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload res_parking.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionAssociatedEvent(parking_lot.id, extension.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, parking_lot, extension):
        self.send_sysconfd_handlers()
        event = ParkingLotExtensionDissociatedEvent(parking_lot.id, extension.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ParkingLotExtensionNotifier(bus, sysconfd)
