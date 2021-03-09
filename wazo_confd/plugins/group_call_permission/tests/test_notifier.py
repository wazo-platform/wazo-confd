# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from uuid import uuid4

from xivo_bus.resources.group_call_permission.event import (
    GroupCallPermissionAssociatedEvent,
    GroupCallPermissionDissociatedEvent,
)
from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from ..notifier import GroupCallPermissionNotifier


class TestGroupCallPermissionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.call_permission = Mock(CallPermission, id=4)
        self.group = Mock(Group, id=5, uuid=uuid4())

        self.notifier = GroupCallPermissionNotifier(self.bus)

    def test_when_call_permission_associate_to_group_then_event_sent_on_bus(self):
        expected_event = GroupCallPermissionAssociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            call_permission_id=self.call_permission.id,
        )

        self.notifier.associated(self.group, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_permission_dissociate_to_group_then_event_sent_on_bus(self):
        expected_event = GroupCallPermissionDissociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            call_permission_id=self.call_permission.id,
        )

        self.notifier.dissociated(self.group, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
