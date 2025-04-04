# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.parking_lot.event import (
    ParkingLotCreatedEvent,
    ParkingLotDeletedEvent,
    ParkingLotEditedEvent,
)

from ..notifier import ParkingLotNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload res_parking.so']}


class TestParkingLotNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.parking_lot = Mock(id=1234, tenant_uuid=uuid4())

        self.notifier = ParkingLotNotifier(self.bus, self.sysconfd)

    def test_when_parking_lot_created_then_res_parking_reloaded(self):
        self.notifier.created(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_created_then_event_sent_on_bus(self):
        expected_event = ParkingLotCreatedEvent(
            self.parking_lot.id, self.parking_lot.tenant_uuid
        )

        self.notifier.created(self.parking_lot)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_parking_lot_edited_then_res_parking_reloaded(self):
        self.notifier.edited(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_edited_then_event_sent_on_bus(self):
        expected_event = ParkingLotEditedEvent(
            self.parking_lot.id, self.parking_lot.tenant_uuid
        )

        self.notifier.edited(self.parking_lot)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_parking_lot_deleted_then_res_parking_reloaded(self):
        self.notifier.deleted(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_deleted_then_event_sent_on_bus(self):
        expected_event = ParkingLotDeletedEvent(
            self.parking_lot.id, self.parking_lot.tenant_uuid
        )

        self.notifier.deleted(self.parking_lot)

        self.bus.queue_event.assert_called_once_with(expected_event)
