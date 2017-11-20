# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.wizard.event import CreateWizardEvent

from xivo_confd.plugins.wizard.notifier import WizardNotifier


class TestWizardNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()

        self.notifier = WizardNotifier(self.bus)

    def test_when_wizard_created_then_event_sent_on_bus(self):
        expected_event = CreateWizardEvent()

        self.notifier.created()

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
