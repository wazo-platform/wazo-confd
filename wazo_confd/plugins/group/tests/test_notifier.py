# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from uuid import uuid4
from mock import Mock

from xivo_bus.resources.group.event import (
    CreateGroupEvent,
    DeleteGroupEvent,
    EditGroupEvent,
)

from ..notifier import GroupNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}


class TestGroupNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        group_id = 1234
        group_uuid = uuid4()
        self.group = Mock(id=group_id, uuid=group_uuid)
        self.group_serialized = {'id': group_id, 'uuid': str(group_uuid)}

        self.notifier = GroupNotifier(self.bus, self.sysconfd)

    def test_when_group_created_then_dialplan_reloaded(self):
        self.notifier.created(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_created_then_event_sent_on_bus(self):
        expected_event = CreateGroupEvent(**self.group_serialized)

        self.notifier.created(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_group_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_edited_then_event_sent_on_bus(self):
        expected_event = EditGroupEvent(**self.group_serialized)

        self.notifier.edited(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_group_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.group)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_group_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteGroupEvent(**self.group_serialized)

        self.notifier.deleted(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
