# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserAgentNotifier


class TestAgentNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.agent = Mock(id=1)
        self.user = Mock(User, uuid='abcd-1234', id=2)

        self.notifier = UserAgentNotifier(self.bus, self.sysconfd)

    def _expected_handlers(self):
        return {
            'ctibus': ['xivo[user,edit,2]'],
            'ipbx': [],
            'agentbus': [],
        }

    def test_when_agent_associate_to_user_then_call_expected_handlers(self):
        self.notifier.associated(self.user, self.agent)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._expected_handlers())

    def test_when_agent_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentAssociatedEvent(self.user.uuid, self.agent.id)

        self.notifier.associated(self.user, self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_agent_dissociate_to_user_then_call_expected_handlers(self):
        self.notifier.dissociated(self.user, self.agent)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self._expected_handlers())

    def test_when_agent_dissociate_to_user_then_event_sent_on_bus(self):
        expected_event = UserAgentDissociatedEvent(self.user.uuid, self.agent.id)

        self.notifier.dissociated(self.user, self.agent)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
