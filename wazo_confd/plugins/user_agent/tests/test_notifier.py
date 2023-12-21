# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserAgentNotifier


class TestAgentNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.agent = Mock(id=1)
        self.user = Mock(User, uuid='abcd-1234', id=2, tenant_uuid=str(uuid4()))

        self.notifier = UserAgentNotifier(self.bus)

    def test_when_agent_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentAssociatedEvent(
            self.agent.id, self.user.tenant_uuid, self.user.uuid
        )

        self.notifier.associated(self.user, self.agent)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_agent_dissociate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentDissociatedEvent(
            self.agent.id, self.user.tenant_uuid, self.user.uuid
        )

        self.notifier.dissociated(self.user, self.agent)

        self.bus.queue_event.assert_called_once_with(expected_event)
