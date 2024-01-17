# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from uuid import uuid4
from unittest.mock import Mock

from wazo_bus.resources.group.event import (
    GroupCreatedEvent,
    GroupDeletedEvent,
    GroupEditedEvent,
)

from ..notifier import GroupNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_queue.so']}


class TestGroupNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        group_id = 1234
        group_uuid = uuid4()
        self.group = Mock(id=group_id, uuid=group_uuid, tenant_uuid=uuid4())
        self.group_serialized = {'id': group_id, 'uuid': str(group_uuid)}
        self.expected_headers = {'tenant_uuid': str(self.group.tenant_uuid)}

        self.notifier = GroupNotifier(self.bus, self.sysconfd)

    def test_when_group_created_then_dialplan_reloaded(self):
        self.notifier.created(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_created_then_event_sent_on_bus(self):
        expected_event = GroupCreatedEvent(
            self.group_serialized, self.group.tenant_uuid
        )

        self.notifier.created(self.group)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_group_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_edited_then_event_sent_on_bus(self):
        expected_event = GroupEditedEvent(self.group_serialized, self.group.tenant_uuid)

        self.notifier.edited(self.group)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_group_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_deleted_then_event_sent_on_bus(self):
        expected_event = GroupDeletedEvent(
            self.group_serialized, self.group.tenant_uuid
        )

        self.notifier.deleted(self.group)

        self.bus.queue_event.assert_called_once_with(expected_event)
