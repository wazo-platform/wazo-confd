# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.user_external_app.event import (
    UserExternalAppCreatedEvent,
    UserExternalAppDeletedEvent,
    UserExternalAppEditedEvent,
)

from ..notifier import UserExternalAppNotifier


class TestUserExternalAppNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.external_app = Mock()
        self.external_app.name = 'limitation of mock instantiation with name ...'
        self.tenant_uuid = uuid4()
        self.app_serialized = {'name': self.external_app.name}

        self.notifier = UserExternalAppNotifier(self.bus)

    def test_when_external_app_created_then_event_sent_on_bus(self):
        expected_event = UserExternalAppCreatedEvent(
            self.app_serialized, self.tenant_uuid
        )

        self.notifier.created(self.external_app, self.tenant_uuid)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_external_app_edited_then_event_sent_on_bus(self):
        expected_event = UserExternalAppEditedEvent(
            self.app_serialized, self.tenant_uuid
        )

        self.notifier.edited(self.external_app, self.tenant_uuid)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_external_app_deleted_then_event_sent_on_bus(self):
        expected_event = UserExternalAppDeletedEvent(
            self.app_serialized, self.tenant_uuid
        )

        self.notifier.deleted(self.external_app, self.tenant_uuid)

        self.bus.queue_event.assert_called_once_with(expected_event)
