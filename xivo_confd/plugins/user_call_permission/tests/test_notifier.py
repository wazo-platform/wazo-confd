# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest

from mock import Mock

from xivo_bus.resources.user_call_permission.event import (UserCallPermissionAssociatedEvent,
                                                           UserCallPermissionDissociatedEvent)
from xivo_confd.plugins.user_call_permission.notifier import UserCallPermissionNotifier

from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestUserCallPermissionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.call_permission = Mock(CallPermission, id=4)
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserCallPermissionNotifier(self.bus)

    def test_when_call_permission_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserCallPermissionAssociatedEvent(self.user.uuid, self.call_permission.id)

        self.notifier.associated(self.user, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_call_permission_dissociate_to_user_then_event_sent_on_bus(self):
        expected_event = UserCallPermissionDissociatedEvent(self.user.uuid, self.call_permission.id)

        self.notifier.dissociated(self.user, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
