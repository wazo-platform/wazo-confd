# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.wizard.event import CreateWizardEvent

from ..notifier import WizardNotifier


class TestWizardNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()

        self.notifier = WizardNotifier(self.bus)

    def test_when_wizard_created_then_event_sent_on_bus(self):
        expected_event = CreateWizardEvent()

        self.notifier.created()

        self.bus.send_bus_event.assert_called_once_with(expected_event)
