# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.user.event import UserFallbackEditedEvent
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserFallbackNotifier


class TestUserFallbackNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, id=1, uuid='abcd-1234', tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.user.tenant_uuid}

        self.notifier = UserFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = UserFallbackEditedEvent(
            self.user.id, self.user.tenant_uuid, self.user.uuid
        )

        self.notifier.edited(self.user)

        self.bus.queue_event.assert_called_once_with(expected_event)
