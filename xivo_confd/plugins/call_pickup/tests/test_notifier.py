# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.call_pickup.event import (
    CreateCallPickupEvent,
    DeleteCallPickupEvent,
    EditCallPickupEvent,
)
from xivo_dao.alchemy.pickup import Pickup as CallPickup

from ..notifier import CallPickupNotifier


class TestCallPickupNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.call_pickup = Mock(CallPickup, id=1234)

        self.notifier = CallPickupNotifier(self.bus)

    def test_when_call_pickup_created_then_event_sent_on_bus(self):
        expected_event = CreateCallPickupEvent(self.call_pickup.id)

        self.notifier.created(self.call_pickup)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_pickup_edited_then_event_sent_on_bus(self):
        expected_event = EditCallPickupEvent(self.call_pickup.id)

        self.notifier.edited(self.call_pickup)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_pickup_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCallPickupEvent(self.call_pickup.id)

        self.notifier.deleted(self.call_pickup)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
