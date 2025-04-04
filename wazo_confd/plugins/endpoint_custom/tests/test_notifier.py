# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.endpoint_custom.event import (
    CustomEndpointCreatedEvent,
    CustomEndpointDeletedEvent,
    CustomEndpointEditedEvent,
)
from xivo_dao.alchemy.usercustom import UserCustom as Custom

from ..notifier import CustomEndpointNotifier


class TestCustomEndpointNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.custom = Mock(
            Custom,
            id=1,
            tenant_uuid=str(uuid.uuid4),
            interface='custom/custom',
            trunk={'id': 2},
            line=None,
        )
        self.custom_serialized = {
            'id': self.custom.id,
            'tenant_uuid': self.custom.tenant_uuid,
            'interface': self.custom.interface,
            'trunk': self.custom.trunk,
            'line': self.custom.line,
        }
        self.notifier = CustomEndpointNotifier(self.bus)

    def test_when_custom_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CustomEndpointCreatedEvent(
            self.custom_serialized, self.custom.tenant_uuid
        )

        self.notifier.created(self.custom)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = CustomEndpointEditedEvent(
            self.custom_serialized, self.custom.tenant_uuid
        )

        self.notifier.edited(self.custom)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = CustomEndpointDeletedEvent(
            self.custom_serialized, self.custom.tenant_uuid
        )

        self.notifier.deleted(self.custom)

        self.bus.queue_event.assert_called_once_with(expected_event)
