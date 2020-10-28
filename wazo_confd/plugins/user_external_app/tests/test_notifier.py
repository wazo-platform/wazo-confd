# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.external_app.event import (
    CreateUserExternalAppEvent,
    DeleteUserExternalAppEvent,
    EditUserExternalAppEvent,
)

from ..notifier import UserExternalAppNotifier


class TestUserExternalAppNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.external_app = Mock()
        self.external_app.name = 'limitation of mock instantiation with name ...'
        self.app_serialized = {'name': self.external_app.name}

        self.notifier = UserExternalAppNotifier(self.bus)

    def test_when_external_app_created_then_event_sent_on_bus(self):
        expected_event = CreateUserExternalAppEvent(self.app_serialized)

        self.notifier.created(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_external_app_edited_then_event_sent_on_bus(self):
        expected_event = EditUserExternalAppEvent(self.app_serialized)

        self.notifier.edited(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_external_app_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteUserExternalAppEvent(self.app_serialized)

        self.notifier.deleted(self.external_app)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
