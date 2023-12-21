# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from xivo_bus.resources.hep.event import HEPGeneralEditedEvent

from ..notifier import HEPConfigurationNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload res_hep.so']}


class TestHEPConfigurationNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.hep = Mock()
        self.sysconfd = Mock()

        self.notifier = HEPConfigurationNotifier(self.bus, self.sysconfd)

    def test_when_hep_general_edited_then_event_sent_on_bus(self):
        expected_event = HEPGeneralEditedEvent()

        self.notifier.edited('general', self.hep)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_hep_general_edited_then_hep_reloaded(self):
        self.notifier.edited('general', self.hep)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
