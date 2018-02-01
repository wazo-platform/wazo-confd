# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.call_filter_user.event import (
    CallFilterRecipientUsersAssociatedEvent,
    CallFilterSurrogateUsersAssociatedEvent,
)
from xivo_dao.alchemy.callfilter import Callfilter as CallFilter
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import CallFilterUserNotifier


class TestCallFilterRecipientUserNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user1 = Mock(User, uuid='abcd-1234')
        self.user2 = Mock(User, uuid='efgh-5678')
        self.call_filter = Mock(CallFilter, id=3)

        self.notifier = CallFilterUserNotifier(self.bus)

    def test_recipient_users_associate_then_bus_event(self):
        expected_event = CallFilterRecipientUsersAssociatedEvent(
            self.call_filter.id,
            [self.user1.uuid, self.user2.uuid]
        )

        self.notifier.recipient_users_associated(self.call_filter, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_surrogate_users_associate_then_bus_event(self):
        expected_event = CallFilterSurrogateUsersAssociatedEvent(
            self.call_filter.id,
            [self.user1.uuid, self.user2.uuid]
        )

        self.notifier.surrogate_users_associated(self.call_filter, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)
