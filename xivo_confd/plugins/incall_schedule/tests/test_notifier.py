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

from xivo_bus.resources.incall_schedule.event import (IncallScheduleAssociatedEvent,
                                                      IncallScheduleDissociatedEvent)
from ..notifier import IncallScheduleNotifier

from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.schedule import Schedule


class TestIncallScheduleNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(Schedule, id=1)
        self.incall = Mock(Incall, id=2)

        self.notifier = IncallScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = IncallScheduleAssociatedEvent(self.incall.id, self.schedule.id)

        self.notifier.associated(self.incall, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_dissociate_then_bus_event(self):
        expected_event = IncallScheduleDissociatedEvent(self.incall.id, self.schedule.id)

        self.notifier.dissociated(self.incall, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
