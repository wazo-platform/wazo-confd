# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.paging_user.event import (
    PagingCallerUsersAssociatedEvent,
    PagingMemberUsersAssociatedEvent,
)
from xivo_dao.alchemy.paging import Paging
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import PagingUserNotifier


class TestPagingUserNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user1 = Mock(User, uuid='abcd-1234')
        self.user2 = Mock(User, uuid='efgh-5678')
        self.paging = Mock(Paging, id=3, tenant_uuid=uuid4())

        self.notifier = PagingUserNotifier(self.bus)

    def test_associate_caller_then_bus_event(self):
        expected_event = PagingCallerUsersAssociatedEvent(
            self.paging.id, [self.user1.uuid, self.user2.uuid], self.paging.tenant_uuid
        )

        self.notifier.callers_associated(self.paging, [self.user1, self.user2])

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_member_then_bus_event(self):
        expected_event = PagingMemberUsersAssociatedEvent(
            self.paging.id, [self.user1.uuid, self.user2.uuid], self.paging.tenant_uuid
        )

        self.notifier.members_associated(self.paging, [self.user1, self.user2])

        self.bus.queue_event.assert_called_once_with(expected_event)
