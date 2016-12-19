# -*- coding: utf-8 -*-

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

import unittest

from mock import Mock

from xivo_bus.resources.parking_lot_extension.event import (ParkingLotExtensionAssociatedEvent,
                                                            ParkingLotExtensionDissociatedEvent)
from ..notifier import ParkingLotExtensionNotifier

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.parking_lot import ParkingLot


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload res_parking.so'],
                     'agentbus': []}


class TestParkingLotExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.parking_lot = Mock(ParkingLot, id=2)

        self.notifier = ParkingLotExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ParkingLotExtensionAssociatedEvent(self.parking_lot.id, self.extension.id)

        self.notifier.associated(self.parking_lot, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = ParkingLotExtensionDissociatedEvent(self.parking_lot.id, self.extension.id)

        self.notifier.dissociated(self.parking_lot, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
