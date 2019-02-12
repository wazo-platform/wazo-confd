# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from xivo_bus.resources.high_availability.event import (
    EditHAEvent,
)

from ..notifier import HANotifier


class TestHANotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.notifier = HANotifier(self.bus, self.sysconfd)

    def test_when_high_availability_edited_then_event_sent_on_bus(self):
        expected_event = EditHAEvent()

        self.notifier.edited()

        self.bus.send_bus_event.assert_called_once_with(expected_event)
        self.sysconfd.update_ha_config.assert_called_once_with()
