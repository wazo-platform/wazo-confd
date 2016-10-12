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

from xivo_bus.resources.outcall_trunk.event import OutcallTrunksAssociatedEvent
from ..notifier import OutcallTrunkNotifier

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TestOutcallTrunkNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.outcall = Mock(Outcall, id=2)
        self.trunk = Mock(Trunk, id=1)

        self.notifier = OutcallTrunkNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = OutcallTrunksAssociatedEvent(self.outcall.id, [self.trunk.id])

        self.notifier.associated_all_trunks(self.outcall, [self.trunk])

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
