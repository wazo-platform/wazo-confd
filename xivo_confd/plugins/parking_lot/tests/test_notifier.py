# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.parking_lot.event import (
    CreateParkingLotEvent,
    DeleteParkingLotEvent,
    EditParkingLotEvent,
)

from ..notifier import ParkingLotNotifier

EXPECTED_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload res_parking.so'],
                     'agentbus': []}


class TestParkingLotNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.parking_lot = Mock(id=1234)

        self.notifier = ParkingLotNotifier(self.bus, self.sysconfd)

    def test_when_parking_lot_created_then_res_parking_reloaded(self):
        self.notifier.created(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_created_then_event_sent_on_bus(self):
        expected_event = CreateParkingLotEvent(self.parking_lot.id)

        self.notifier.created(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_parking_lot_edited_then_res_parking_reloaded(self):
        self.notifier.edited(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_edited_then_event_sent_on_bus(self):
        expected_event = EditParkingLotEvent(self.parking_lot.id)

        self.notifier.edited(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_parking_lot_deleted_then_res_parking_reloaded(self):
        self.notifier.deleted(self.parking_lot)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_parking_lot_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteParkingLotEvent(self.parking_lot.id)

        self.notifier.deleted(self.parking_lot)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
