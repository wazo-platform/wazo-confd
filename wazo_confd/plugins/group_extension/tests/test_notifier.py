# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.group_extension.event import (
    GroupExtensionAssociatedEvent,
    GroupExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from ..notifier import GroupExtensionNotifier

SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload']}


class TestGroupExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.group = Mock(Group, id=2, uuid=uuid4(), tenant_uuid=uuid4())

        self.notifier = GroupExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = GroupExtensionAssociatedEvent(
            self.group.id, self.group.uuid, self.extension.id, self.group.tenant_uuid
        )

        self.notifier.associated(self.group, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = GroupExtensionDissociatedEvent(
            self.group.id,
            self.group.uuid,
            self.extension.id,
            self.group.tenant_uuid,
        )

        self.notifier.dissociated(self.group, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
