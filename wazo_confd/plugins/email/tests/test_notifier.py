# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from xivo_bus.resources.email.event import EmailConfigUpdatedEvent

from ..notifier import EmailConfigNotifier


class TestEmailConfigNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()

        self.notifier = EmailConfigNotifier(self.bus, self.sysconfd)

    def test_when_email_config_edited_then_event_sent_on_bus(self):
        expected_event = EmailConfigUpdatedEvent()

        self.notifier.edited()

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_email_config_edited_then_commonconf_regenerated(self):
        self.notifier.edited()
        self.sysconfd.commonconf_generate.assert_called_once_with()
        self.sysconfd.commonconf_apply.assert_called_once_with()
