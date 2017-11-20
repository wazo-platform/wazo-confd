# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
