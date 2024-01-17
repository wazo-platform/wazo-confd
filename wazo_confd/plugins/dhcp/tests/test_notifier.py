# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock
from wazo_bus.resources.dhcp.event import DHCPEditedEvent
from xivo_dao.alchemy.dhcp import Dhcp

from ..notifier import DHCPNotifier


class TestDHCPNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.dhcp = Mock(Dhcp)

        self.notifier = DHCPNotifier(self.bus, self.sysconfd)

    def test_when_dhcp_edited_then_event_sent_on_bus(self):
        expected_event = DHCPEditedEvent()

        self.notifier.edited()

        self.bus.queue_event.assert_called_once_with(expected_event)
        self.sysconfd.commonconf_generate.assert_called_once_with()
        self.sysconfd.commonconf_apply.assert_called_once_with()
