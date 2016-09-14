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

from xivo_bus.resources.incall.event import (CreateIncallEvent,
                                             EditIncallEvent,
                                             DeleteIncallEvent)
from xivo_dao.alchemy.incall import Incall

from ..notifier import IncallNotifier


class TestIncallNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.incall = Mock(Incall, id=1234)

        self.notifier = IncallNotifier(self.bus)

    def test_when_incall_created_then_event_sent_on_bus(self):
        expected_event = CreateIncallEvent(self.incall.id)

        self.notifier.created(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_incall_edited_then_event_sent_on_bus(self):
        expected_event = EditIncallEvent(self.incall.id)

        self.notifier.edited(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_incall_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteIncallEvent(self.incall.id)

        self.notifier.deleted(self.incall)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
