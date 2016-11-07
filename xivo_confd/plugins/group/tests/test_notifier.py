# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from xivo_bus.resources.group.event import (CreateGroupEvent,
                                            EditGroupEvent,
                                            DeleteGroupEvent)

from ..notifier import GroupNotifier

EXPECTED_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload app_queue.so'],
                     'agentbus': []}


class TestGroupNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.group = Mock(id=1234)

        self.notifier = GroupNotifier(self.bus, self.sysconfd)

    def test_when_group_created_then_dialplan_reloaded(self):
        self.notifier.created(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_created_then_event_sent_on_bus(self):
        expected_event = CreateGroupEvent(self.group.id)

        self.notifier.created(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_group_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_edited_then_event_sent_on_bus(self):
        expected_event = EditGroupEvent(self.group.id)

        self.notifier.edited(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_group_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteGroupEvent(self.group.id)

        self.notifier.deleted(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
