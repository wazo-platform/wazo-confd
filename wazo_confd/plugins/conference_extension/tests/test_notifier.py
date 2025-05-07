# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.conference_extension.event import (
    ConferenceExtensionAssociatedEvent,
    ConferenceExtensionDissociatedEvent,
)
from xivo_dao.alchemy.conference import Conference
from xivo_dao.alchemy.extension import Extension

from ..notifier import ConferenceExtensionNotifier

SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload']}


class TestConferenceExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.conference = Mock(Conference, id=2, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.conference.tenant_uuid}

        self.notifier = ConferenceExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ConferenceExtensionAssociatedEvent(
            self.conference.id, self.extension.id, self.conference.tenant_uuid
        )

        self.notifier.associated(self.conference, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.conference, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = ConferenceExtensionDissociatedEvent(
            self.conference.id, self.extension.id, self.conference.tenant_uuid
        )

        self.notifier.dissociated(self.conference, self.extension)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.conference, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
