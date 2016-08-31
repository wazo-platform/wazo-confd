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

from xivo_bus.resources.trunk.event import (CreateTrunkEvent,
                                            EditTrunkEvent,
                                            DeleteTrunkEvent)

from xivo_confd.plugins.trunk.notifier import TrunkNotifier

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TestTrunkNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.trunk = Mock(Trunk, id=1234)

        self.notifier = TrunkNotifier(self.bus)

    def test_when_trunk_created_then_event_sent_on_bus(self):
        expected_event = CreateTrunkEvent(self.trunk.id)

        self.notifier.created(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_trunk_edited_then_event_sent_on_bus(self):
        expected_event = EditTrunkEvent(self.trunk.id)

        self.notifier.edited(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_trunk_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteTrunkEvent(self.trunk.id)

        self.notifier.deleted(self.trunk)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
