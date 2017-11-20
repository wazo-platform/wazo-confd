# -*- coding: UTF-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.parking_lot.event import (CreateParkingLotEvent,
                                                  EditParkingLotEvent,
                                                  DeleteParkingLotEvent)


class ParkingLotNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload res_parking.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, parking_lot):
        self.send_sysconfd_handlers()
        event = CreateParkingLotEvent(parking_lot.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, parking_lot):
        self.send_sysconfd_handlers()
        event = EditParkingLotEvent(parking_lot.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, parking_lot):
        self.send_sysconfd_handlers()
        event = DeleteParkingLotEvent(parking_lot.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ParkingLotNotifier(bus, sysconfd)
