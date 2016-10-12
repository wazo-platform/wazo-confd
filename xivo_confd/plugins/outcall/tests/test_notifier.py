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

from xivo_bus.resources.outcall.event import (CreateOutcallEvent,
                                              EditOutcallEvent,
                                              DeleteOutcallEvent)
from xivo_dao.alchemy.outcall import Outcall

from ..notifier import OutcallNotifier


class TestOutcallNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.outcall = Mock(Outcall, id=1234)

        self.notifier = OutcallNotifier(self.bus)

    def test_when_outcall_created_then_event_sent_on_bus(self):
        expected_event = CreateOutcallEvent(self.outcall.id)

        self.notifier.created(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_outcall_edited_then_event_sent_on_bus(self):
        expected_event = EditOutcallEvent(self.outcall.id)

        self.notifier.edited(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_outcall_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteOutcallEvent(self.outcall.id)

        self.notifier.deleted(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
