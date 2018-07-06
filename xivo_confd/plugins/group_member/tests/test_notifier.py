# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.group_member.event import (
    GroupMemberUsersAssociatedEvent,
    GroupMemberExtensionsAssociatedEvent,
)

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
        self.member_user1 = Mock(user=Mock(uuid='abcd-1234'))
        self.member_user2 = Mock(user=Mock(uuid='efgh-5678'))
        self.member_extension1 = Mock(extension=Mock(exten='1234', context='default'))
        self.member_extension2 = Mock(extension=Mock(exten='5678', context='other'))
        self.group = Mock(id=3)

        self.notifier = GroupMemberNotifier(self.bus, self.sysconfd)

    def test_associate_users_then_bus_event(self):
        expected_event = GroupMemberUsersAssociatedEvent(
            self.group.id,
            [self.member_user1.user.uuid, self.member_user2.user.uuid],
        )

        self.notifier.users_associated(self.group, [self.member_user1, self.member_user2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_users_then_sysconfd_event(self):
        self.notifier.users_associated(self.group, [self.member_user1, self.member_user2])

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_associate_extensions_then_bus_event(self):
        expected_event = GroupMemberExtensionsAssociatedEvent(
            self.group.id,
            [
                {
                    'exten': self.member_extension1.extension.exten,
                    'context': self.member_extension1.extension.context
                },
                {
                    'exten': self.member_extension2.extension.exten,
                    'context': self.member_extension2.extension.context
                },
            ]
        )

        self.notifier.extensions_associated(self.group, [self.member_extension1, self.member_extension2])

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_extensions_then_sysconfd_event(self):
        self.notifier.extensions_associated(self.group, [self.member_extension1, self.member_extension2])

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
