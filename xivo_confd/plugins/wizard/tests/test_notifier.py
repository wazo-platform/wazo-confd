# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
