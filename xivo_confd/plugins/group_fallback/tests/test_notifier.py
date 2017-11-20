# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.group.event import EditGroupFallbackEvent
from ..notifier import GroupFallbackNotifier

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group


class TestGroupFallbackNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.group = Mock(Group, id=1)

        self.notifier = GroupFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = EditGroupFallbackEvent(self.group.id)

        self.notifier.edited(self.group)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
