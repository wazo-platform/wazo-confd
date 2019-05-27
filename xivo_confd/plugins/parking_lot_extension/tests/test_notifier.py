# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.parking_lot_extension.event import (
    ParkingLotExtensionAssociatedEvent,
    ParkingLotExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.parking_lot import ParkingLot

from ..notifier import ParkingLotExtensionNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_parking.so'],
    'agentbus': [],
}


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

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = ParkingLotExtensionDissociatedEvent(self.parking_lot.id, self.extension.id)

        self.notifier.dissociated(self.parking_lot, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
