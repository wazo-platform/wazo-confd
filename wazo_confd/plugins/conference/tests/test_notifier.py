# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from wazo_bus.resources.conference.event import (
    ConferenceCreatedEvent,
    ConferenceDeletedEvent,
    ConferenceEditedEvent,
)

from ..notifier import ConferenceNotifier

EXPECTED_HANDLERS = {'ipbx': ['module reload app_confbridge.so']}


class TestConferenceNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.conference = Mock(id=1234, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.conference.tenant_uuid}

        self.notifier = ConferenceNotifier(self.bus, self.sysconfd)

    def test_when_conference_created_then_dialplan_reloaded(self):
        self.notifier.created(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_created_then_event_sent_on_bus(self):
        expected_event = ConferenceCreatedEvent(
            self.conference.id, self.conference.tenant_uuid
        )

        self.notifier.created(self.conference)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_conference_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_edited_then_event_sent_on_bus(self):
        expected_event = ConferenceEditedEvent(
            self.conference.id, self.conference.tenant_uuid
        )

        self.notifier.edited(self.conference)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_conference_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_deleted_then_event_sent_on_bus(self):
        expected_event = ConferenceDeletedEvent(
            self.conference.id, self.conference.tenant_uuid
        )

        self.notifier.deleted(self.conference)

        self.bus.queue_event.assert_called_once_with(expected_event)
