# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

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
        self.expected_headers = {'tenant_uuid': str(self.group.tenant_uuid)}

        self.notifier = GroupExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = GroupExtensionAssociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            extension_id=self.extension.id,
        )

        self.notifier.associated(self.group, self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = GroupExtensionDissociatedEvent(
            group_id=self.group.id,
            group_uuid=str(self.group.uuid),
            extension_id=self.extension.id,
        )

        self.notifier.dissociated(self.group, self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
