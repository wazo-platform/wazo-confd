# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.external_app.event import (
    CreateExternalAppEvent,
    DeleteExternalAppEvent,
    EditExternalAppEvent,
)

from ..notifier import ExternalAppNotifier


class TestExternalAppNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.external_app = Mock()
        self.external_app.name = 'limitation of mock instantiation with name ...'
        self.app_serialized = {'name': self.external_app.name}

        self.notifier = ExternalAppNotifier(self.bus)

    def test_when_external_app_created_then_event_sent_on_bus(self):
        expected_event = CreateExternalAppEvent(self.app_serialized)

        self.notifier.created(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_external_app_edited_then_event_sent_on_bus(self):
        expected_event = EditExternalAppEvent(self.app_serialized)

        self.notifier.edited(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_external_app_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteExternalAppEvent(self.app_serialized)

        self.notifier.deleted(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
