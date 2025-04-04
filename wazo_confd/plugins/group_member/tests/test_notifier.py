# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.group_member.event import (
    GroupMemberExtensionsAssociatedEvent,
    GroupMemberUsersAssociatedEvent,
)

from ..notifier import GroupMemberNotifier

SYSCONFD_HANDLERS = {
    'ipbx': [
        'module reload res_pjsip.so',
        'module reload app_queue.so',
        'module reload chan_sccp.so',
    ]
}


class TestGroupMemberUserNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.member_user1 = Mock(user=Mock(uuid='abcd-1234'))
        self.member_user2 = Mock(user=Mock(uuid='efgh-5678'))
        self.member_extension1 = Mock(extension=Mock(exten='1234', context='default'))
        self.member_extension2 = Mock(extension=Mock(exten='5678', context='other'))
        self.group = Mock(id=3, uuid=uuid4(), tenant_uuid=uuid4())

        self.notifier = GroupMemberNotifier(self.bus, self.sysconfd)

    def test_associate_users_then_bus_event(self):
        expected_event = GroupMemberUsersAssociatedEvent(
            self.group.id,
            self.group.uuid,
            [self.member_user1.user.uuid, self.member_user2.user.uuid],
            self.group.tenant_uuid,
        )

        self.notifier.users_associated(
            self.group, [self.member_user1, self.member_user2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_users_then_sysconfd_event(self):
        self.notifier.users_associated(
            self.group, [self.member_user1, self.member_user2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_associate_extensions_then_bus_event(self):
        expected_event = GroupMemberExtensionsAssociatedEvent(
            self.group.id,
            self.group.uuid,
            [
                {
                    'exten': self.member_extension1.extension.exten,
                    'context': self.member_extension1.extension.context,
                },
                {
                    'exten': self.member_extension2.extension.exten,
                    'context': self.member_extension2.extension.context,
                },
            ],
            self.group.tenant_uuid,
        )

        self.notifier.extensions_associated(
            self.group, [self.member_extension1, self.member_extension2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_extensions_then_sysconfd_event(self):
        self.notifier.extensions_associated(
            self.group, [self.member_extension1, self.member_extension2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
