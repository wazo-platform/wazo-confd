# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.group_extension.event import (
    GroupExtensionAssociatedEvent,
    GroupExtensionDissociatedEvent,
)
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from ..notifier import GroupExtensionNotifier

SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['dialplan reload'],
                     'agentbus': []}


class TestGroupExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.group = Mock(Group, id=2)

        self.notifier = GroupExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = GroupExtensionAssociatedEvent(self.group.id, self.extension.id)

        self.notifier.associated(self.group, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = GroupExtensionDissociatedEvent(self.group.id, self.extension.id)

        self.notifier.dissociated(self.group, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.group, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
