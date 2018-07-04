# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.group_member.event import GroupMemberUsersAssociatedEvent

from ..notifier import GroupMemberNotifier


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['sip reload',
                              'module reload app_queue.so',
                              'module reload chan_sccp.so'],
                     'agentbus': []}


class TestGroupMemberUserNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.member1 = Mock(user=Mock(uuid='abcd-1234'))
        self.member2 = Mock(user=Mock(uuid='efgh-5678'))
        self.group = Mock(id=3)

        self.notifier = GroupMemberNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = GroupMemberUsersAssociatedEvent(
            self.group.id,
            [self.member1.user.uuid, self.member2.user.uuid],
        )

        self.notifier.users_associated(self.group, [self.member1, self.member2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.users_associated(self.group, [self.member1, self.member2])

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
