# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.extension_feature.event import EditExtensionFeatureEvent
from xivo_dao.alchemy.extension import Extension

from ..notifier import ExtensionFeatureNotifier


class TestExtensionFeatureNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.extension = Mock(Extension, id=1)

        self.notifier = ExtensionFeatureNotifier(self.sysconfd, self.bus)

    def test_when_extension_edited_then_handlers_sent(self):
        expected_handlers = {'ipbx': ['dialplan reload'], 'agentbus': []}
        updated_fields = ['exten']
        self.notifier.edited(self.extension, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_and_no_change_then_handlers_not_sent(self):
        updated_fields = []

        self.notifier.edited(self.extension, updated_fields)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_extension_edited_then_event_sent_on_bus(self):
        expected_event = EditExtensionFeatureEvent(self.extension.id)
        updated_fields = []

        self.notifier.edited(self.extension, updated_fields)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
