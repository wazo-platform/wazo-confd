# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_bus.resources.paging.event import (CreatePagingEvent,
                                             EditPagingEvent,
                                             DeletePagingEvent)

from ..notifier import PagingNotifier


class TestPagingNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.paging = Mock(id=1234)

        self.notifier = PagingNotifier(self.bus)

    def test_when_paging_created_then_event_sent_on_bus(self):
        expected_event = CreatePagingEvent(self.paging.id)

        self.notifier.created(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_paging_edited_then_event_sent_on_bus(self):
        expected_event = EditPagingEvent(self.paging.id)

        self.notifier.edited(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_paging_deleted_then_event_sent_on_bus(self):
        expected_event = DeletePagingEvent(self.paging.id)

        self.notifier.deleted(self.paging)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
