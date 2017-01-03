# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from mock import Mock

from xivo_bus.resources.paging_user.event import (PagingMemberUsersAssociatedEvent,
                                                  PagingCallerUsersAssociatedEvent)
from ..notifier import PagingUserNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.paging import Paging


class TestPagingUserNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user1 = Mock(User, uuid='abcd-1234')
        self.user2 = Mock(User, uuid='efgh-5678')
        self.paging = Mock(Paging, id=3)

        self.notifier = PagingUserNotifier(self.bus)

    def test_associate_caller_then_bus_event(self):
        expected_event = PagingCallerUsersAssociatedEvent(self.paging.id, [self.user1.uuid, self.user2.uuid])

        self.notifier.callers_associated(self.paging, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_associate_member_then_bus_event(self):
        expected_event = PagingMemberUsersAssociatedEvent(self.paging.id, [self.user1.uuid, self.user2.uuid])

        self.notifier.members_associated(self.paging, [self.user1, self.user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
