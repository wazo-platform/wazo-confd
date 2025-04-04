# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.call_filter_user.event import (
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
        self.call_filter = Mock(CallFilter, id=3, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.call_filter.tenant_uuid}
        self.notifier = CallFilterUserNotifier(self.bus)

    def test_recipient_users_associate_then_bus_event(self):
        expected_event = CallFilterRecipientUsersAssociatedEvent(
            self.call_filter.id,
            [self.user1.uuid, self.user2.uuid],
            self.call_filter.tenant_uuid,
        )

        self.notifier.recipient_users_associated(
            self.call_filter, [self.user1, self.user2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_surrogate_users_associate_then_bus_event(self):
        expected_event = CallFilterSurrogateUsersAssociatedEvent(
            self.call_filter.id,
            [self.user1.uuid, self.user2.uuid],
            self.call_filter.tenant_uuid,
        )

        self.notifier.surrogate_users_associated(
            self.call_filter, [self.user1, self.user2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)
