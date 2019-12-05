# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid

from mock import Mock

from xivo_bus.resources.endpoint_custom.event import (
    CreateCustomEndpointEvent,
    DeleteCustomEndpointEvent,
    EditCustomEndpointEvent,
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
        expected_event = CreateCustomEndpointEvent(self.custom_serialized)

        self.notifier.created(self.custom)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditCustomEndpointEvent(self.custom_serialized)

        self.notifier.edited(self.custom)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_custom_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteCustomEndpointEvent(self.custom_serialized)

        self.notifier.deleted(self.custom)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
