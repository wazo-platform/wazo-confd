# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from uuid import uuid4
from mock import Mock

from xivo_bus.resources.group.event import EditGroupFallbackEvent
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from ..notifier import GroupFallbackNotifier


class TestGroupFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.group = Mock(Group, id=1, uuid=uuid4(), tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.group.tenant_uuid)}

        self.notifier = GroupFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = EditGroupFallbackEvent(
            id=self.group.id, uuid=str(self.group.uuid)
        )

        self.notifier.edited(self.group)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
