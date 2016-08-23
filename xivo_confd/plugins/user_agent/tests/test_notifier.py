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

from ..notifier import UserAgentNotifier

from xivo_bus.resources.user_agent.event import (UserAgentAssociatedEvent,
                                                 UserAgentDissociatedEvent)
from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestAgentNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.agent = Mock(id='1')
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserAgentNotifier(self.bus)

    def test_when_agent_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentAssociatedEvent(self.user.uuid, self.agent.id)

        self.notifier.associated(self.user, self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_agent_dissociate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentDissociatedEvent(self.user.uuid, self.agent.id)

        self.notifier.dissociated(self.user, self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
