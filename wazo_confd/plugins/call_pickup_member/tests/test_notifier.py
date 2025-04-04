# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.call_pickup_member.event import (
    CallPickupInterceptorGroupsAssociatedEvent,
    CallPickupInterceptorUsersAssociatedEvent,
    CallPickupTargetGroupsAssociatedEvent,
    CallPickupTargetUsersAssociatedEvent,
)
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group
from xivo_dao.alchemy.pickup import Pickup as CallPickup
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import CallPickupMemberNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
}


class TestCallPickupInterceptorUserNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.user1 = Mock(User, uuid='abcd-1234')
        self.user2 = Mock(User, uuid='efgh-5678')
        self.group1 = Mock(Group, uuid='abcd-1234')
        self.group2 = Mock(Group, uuid='efgh-5678')
        self.call_pickup = Mock(CallPickup, id=3, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.call_pickup.tenant_uuid}

        self.notifier = CallPickupMemberNotifier(self.bus, self.sysconfd)

    def test_interceptor_users_associate_then_bus_event(self):
        expected_event = CallPickupInterceptorUsersAssociatedEvent(
            self.call_pickup.id,
            [self.user1.uuid, self.user2.uuid],
            self.call_pickup.tenant_uuid,
        )

        self.notifier.interceptor_users_associated(
            self.call_pickup, [self.user1, self.user2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_interceptor_users_associate_then_sysconfd_event(self):
        self.notifier.interceptor_users_associated(
            self.call_pickup, [self.user1, self.user2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_target_users_associate_then_bus_event(self):
        expected_event = CallPickupTargetUsersAssociatedEvent(
            self.call_pickup.id,
            [self.user1.uuid, self.user2.uuid],
            self.call_pickup.tenant_uuid,
        )

        self.notifier.target_users_associated(
            self.call_pickup, [self.user1, self.user2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_target_users_associate_then_sysconfd_event(self):
        self.notifier.target_users_associated(
            self.call_pickup, [self.user1, self.user2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_interceptor_groups_associate_then_bus_event(self):
        expected_event = CallPickupInterceptorGroupsAssociatedEvent(
            self.call_pickup.id,
            [self.group1.id, self.group2.id],
            self.call_pickup.tenant_uuid,
        )

        self.notifier.interceptor_groups_associated(
            self.call_pickup, [self.group1, self.group2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_interceptor_groups_associate_then_sysconfd_event(self):
        self.notifier.interceptor_groups_associated(
            self.call_pickup, [self.group1, self.group2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_target_groups_associate_then_bus_event(self):
        expected_event = CallPickupTargetGroupsAssociatedEvent(
            self.call_pickup.id,
            [self.group1.id, self.group2.id],
            self.call_pickup.tenant_uuid,
        )

        self.notifier.target_groups_associated(
            self.call_pickup, [self.group1, self.group2]
        )

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_target_groups_associate_then_sysconfd_event(self):
        self.notifier.target_groups_associated(
            self.call_pickup, [self.group1, self.group2]
        )

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
