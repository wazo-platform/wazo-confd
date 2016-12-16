# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
