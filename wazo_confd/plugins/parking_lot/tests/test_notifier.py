# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.parking_lot.event import (
    CreateParkingLotEvent,
    DeleteParkingLotEvent,
    EditParkingLotEvent,
)

from ..notifier import ParkingLotNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload res_parking.so']}


class TestParkingLotNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.parking_lot = Mock(id=1234, tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.parking_lot.tenant_uuid)}

        self.notifier = ParkingLotNotifier(self.bus, self.sysconfd)

    def test_when_parking_lot_created_then_res_parking_reloaded(self):
        self.notifier.created(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_created_then_event_sent_on_bus(self):
        expected_event = CreateParkingLotEvent(self.parking_lot.id)

        self.notifier.created(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_parking_lot_edited_then_res_parking_reloaded(self):
        self.notifier.edited(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_edited_then_event_sent_on_bus(self):
        expected_event = EditParkingLotEvent(self.parking_lot.id)

        self.notifier.edited(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_parking_lot_deleted_then_res_parking_reloaded(self):
        self.notifier.deleted(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteParkingLotEvent(self.parking_lot.id)

        self.notifier.deleted(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
