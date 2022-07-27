# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.parking_lot_extension.event import (
    ParkingLotExtensionAssociatedEvent,
    ParkingLotExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.parking_lot import ParkingLot

from ..notifier import ParkingLotExtensionNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload res_parking.so']}


class TestParkingLotExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.parking_lot = Mock(ParkingLot, id=2, tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.parking_lot.tenant_uuid)}

        self.notifier = ParkingLotExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ParkingLotExtensionAssociatedEvent(
            self.parking_lot.id, self.extension.id
        )

        self.notifier.associated(self.parking_lot, self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = ParkingLotExtensionDissociatedEvent(
            self.parking_lot.id, self.extension.id
        )

        self.notifier.dissociated(self.parking_lot, self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.parking_lot, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
