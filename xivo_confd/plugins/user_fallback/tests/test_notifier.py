# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from xivo_bus.resources.user.event import EditUserFallbackEvent
from ..notifier import UserFallbackNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestUserFallbackNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, id=1, uuid='abcd-1234')

        self.notifier = UserFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = EditUserFallbackEvent(self.user.id, self.user.uuid)

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
