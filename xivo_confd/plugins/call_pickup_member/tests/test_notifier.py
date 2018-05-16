# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.call_pickup_member.event import (
    CallPickupInterceptorUsersAssociatedEvent,
    CallPickupTargetUsersAssociatedEvent,
)
from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import CallPickupUserNotifier


class TestCallPickupInterceptorUserNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user1 = Mock(User, uuid='abcd-1234')
        self.user2 = Mock(User, uuid='efgh-5678')
        self.call_pickup = Mock(CallPickup, id=3)

        self.notifier = CallPickupUserNotifier(self.bus)

    def test_interceptor_users_associate_then_bus_event(self):
        expected_event = CallPickupInterceptorUsersAssociatedEvent(
            self.call_pickup.id,
            [self.user1.uuid, self.user2.uuid]
        )

        self.notifier.interceptor_users_associated(self.call_pickup, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_target_users_associate_then_bus_event(self):
        expected_event = CallPickupTargetUsersAssociatedEvent(
            self.call_pickup.id,
            [self.user1.uuid, self.user2.uuid]
        )

        self.notifier.target_users_associated(self.call_pickup, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)
