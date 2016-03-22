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

from xivo_bus.resources.permission.event import (CreatePermissionEvent,
                                                 EditPermissionEvent,
                                                 DeletePermissionEvent)

from xivo_confd.plugins.permission.notifier import PermissionNotifier

from xivo_dao.alchemy.rightcall import RightCall as Permission


class TestPermissionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.permission = Mock(Permission, id=1234)

        self.notifier = PermissionNotifier(self.bus)

    def test_when_permission_created_then_event_sent_on_bus(self):
        expected_event = CreatePermissionEvent(self.permission.id)

        self.notifier.created(self.permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_permission_edited_then_event_sent_on_bus(self):
        expected_event = EditPermissionEvent(self.permission.id)

        self.notifier.edited(self.permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_permission_deleted_then_event_sent_on_bus(self):
        expected_event = DeletePermissionEvent(self.permission.id)

        self.notifier.deleted(self.permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
