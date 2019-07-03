# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.application.event import (
    CreateApplicationEvent,
    DeleteApplicationEvent,
    EditApplicationEvent,
)

from ..notifier import ApplicationNotifier


class TestApplicationNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.application = Mock(
            uuid='00000000-0000-0000-0000-000000000000',
            tenant_uuid='00000000-0000-0000-0000-000000000001',
            dest_node=None,
            destination=None,
            destination_options={},
        )
        self.application.name = 'limitation of mock instantiation with name ...'
        self.expected_body = {
            'uuid': self.application.uuid,
            'name': self.application.name,
            'tenant_uuid': self.application.tenant_uuid,
            'destination': self.application.destination,
            'destination_options': self.application.destination_options,
        }

        self.notifier = ApplicationNotifier(self.bus)

    def test_when_application_created_then_event_sent_on_bus(self):
        expected_event = CreateApplicationEvent(self.expected_body)

        self.notifier.created(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_application_edited_then_event_sent_on_bus(self):
        expected_event = EditApplicationEvent(self.expected_body)

        self.notifier.edited(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_application_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteApplicationEvent(self.expected_body)

        self.notifier.deleted(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
