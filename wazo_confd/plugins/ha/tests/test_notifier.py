# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock
from wazo_bus.resources.ha.event import HAEditedEvent

from ..notifier import HANotifier


class TestHANotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.notifier = HANotifier(self.bus, self.sysconfd)

    def test_when_high_availability_edited_then_event_sent_on_bus(self):
        expected_event = HAEditedEvent()
        ha = {'node_type': 'disabled', 'remote_address': 'slave.example.com'}

        self.notifier.edited(ha)

        self.bus.queue_event.assert_called_once_with(expected_event)
        self.sysconfd.update_ha_config.assert_called_once_with(ha)
