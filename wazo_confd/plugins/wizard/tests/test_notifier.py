# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.wizard.event import WizardCreatedEvent

from ..notifier import WizardNotifier


class TestWizardNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()

        self.notifier = WizardNotifier(self.bus)

    def test_when_wizard_created_then_event_sent_on_bus(self):
        expected_event = WizardCreatedEvent()

        self.notifier.created()

        self.bus.queue_event.assert_called_once_with(expected_event)
