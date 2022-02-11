# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from mock import Mock

from xivo_bus.resources.call_permission.event import (
    CreateCallPermissionEvent,
    DeleteCallPermissionEvent,
    EditCallPermissionEvent,
)
from xivo_dao.alchemy.rightcall import RightCall as CallPermission

from ..notifier import CallPermissionNotifier


class TestCallPermissionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.call_permission = Mock(CallPermission, id=1234, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.call_permission.tenant_uuid}

        self.notifier = CallPermissionNotifier(self.bus)

    def test_when_call_permission_created_then_event_sent_on_bus(self):
        expected_event = CreateCallPermissionEvent(self.call_permission.id)

        self.notifier.created(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_call_permission_edited_then_event_sent_on_bus(self):
        expected_event = EditCallPermissionEvent(self.call_permission.id)

        self.notifier.edited(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_call_permission_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCallPermissionEvent(self.call_permission.id)

        self.notifier.deleted(self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
