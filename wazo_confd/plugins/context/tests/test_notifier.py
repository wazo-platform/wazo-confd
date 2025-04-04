# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.context.event import (
    ContextCreatedEvent,
    ContextDeletedEvent,
    ContextEditedEvent,
)

from ..notifier import ContextNotifier

EXPECTED_HANDLERS = {'ipbx': ['dialplan reload']}


class TestContextNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()

        self.expected_body = {
            'id': 1234,
            'name': 'thecontext',
            'type': 'internal',
            'tenant_uuid': 'de20898b-a485-4123-a0b7-dc4c1e098820',
        }
        self.context = Mock(**self.expected_body)
        self.context.name = self.expected_body['name']
        self.expected_headers = {'tenant_uuid': self.context.tenant_uuid}

        self.notifier = ContextNotifier(self.bus, self.sysconfd)

    def test_when_context_created_then_dialplan_reloaded(self):
        self.notifier.created(self.context)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_context_created_then_event_sent_on_bus(self):
        expected_event = ContextCreatedEvent(
            self.expected_body, self.context.tenant_uuid
        )

        self.notifier.created(self.context)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_context_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.context)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_context_edited_then_event_sent_on_bus(self):
        expected_event = ContextEditedEvent(
            self.expected_body, self.context.tenant_uuid
        )

        self.notifier.edited(self.context)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_context_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.context)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_context_deleted_then_event_sent_on_bus(self):
        expected_event = ContextDeletedEvent(
            self.expected_body, self.context.tenant_uuid
        )

        self.notifier.deleted(self.context)

        self.bus.queue_event.assert_called_once_with(expected_event)
