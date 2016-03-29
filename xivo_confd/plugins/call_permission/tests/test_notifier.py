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

from xivo_bus.resources.call_permission.event import (CreateCallPermissionEvent,
                                                      EditCallPermissionEvent,
                                                      DeleteCallPermissionEvent)

from xivo_confd.plugins.call_permission.notifier import CallPermissionNotifier

from xivo_dao.alchemy.rightcall import RightCall as CallPermission


class TestCallPermissionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.call_permission = Mock(CallPermission, id=1234)

        self.notifier = CallPermissionNotifier(self.bus)

    def test_when_call_permission_created_then_event_sent_on_bus(self):
        expected_event = CreateCallPermissionEvent(self.call_permission.id)

        self.notifier.created(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_call_permission_edited_then_event_sent_on_bus(self):
        expected_event = EditCallPermissionEvent(self.call_permission.id)

        self.notifier.edited(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_call_permission_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCallPermissionEvent(self.call_permission.id)

        self.notifier.deleted(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
