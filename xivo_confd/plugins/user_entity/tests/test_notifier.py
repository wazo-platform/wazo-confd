# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent
from xivo_confd.plugins.user_entity.notifier import UserEntityNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestUserLineNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, uuid='abcd-1234', entity_id='1')

        self.notifier = UserEntityNotifier(self.bus)

    def test_when_entity_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserEntityAssociatedEvent(self.user.uuid, self.user.entity_id)

        self.notifier.associated(self.user, self.user.entity_id)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
