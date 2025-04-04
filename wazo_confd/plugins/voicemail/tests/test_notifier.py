# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock, call
from uuid import uuid4

from hamcrest import assert_that, contains_exactly
from wazo_bus.resources.voicemail.event import (
    UserVoicemailEditedEvent,
    VoicemailCreatedEvent,
    VoicemailDeletedEvent,
    VoicemailEditedEvent,
)
from xivo_dao.alchemy.voicemail import Voicemail

from ..notifier import VoicemailNotifier


class TestVoicemailNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.voicemail = Mock(Voicemail, id=10, users=[], tenant_uuid=str(uuid4()))
        self.notifier = VoicemailNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_created_then_event_sent_on_bus(self):
        expected_event = VoicemailCreatedEvent(
            self.voicemail.id, self.voicemail.tenant_uuid
        )

        self.notifier.created(self.voicemail)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_voicemail_created_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload']}
        self.notifier.created(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_edited_then_event_sent_on_bus(self):
        user = Mock(uuid='abc-123')
        self.voicemail.users = [user]
        expected_event1 = VoicemailEditedEvent(
            self.voicemail.id, self.voicemail.tenant_uuid
        )
        expected_event2 = UserVoicemailEditedEvent(
            self.voicemail.id, self.voicemail.tenant_uuid, user.uuid
        )

        self.notifier.edited(self.voicemail)

        assert_that(
            self.bus.queue_event.call_args_list,
            contains_exactly(
                call(expected_event1),
                call(expected_event2),
            ),
        )

    def test_when_voicemail_edited_then_sysconfd_called(self):
        expected_handlers = {
            'ipbx': [
                'voicemail reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
            ]
        }
        self.notifier.edited(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_deleted_then_event_sent_on_bus(self):
        expected_event = VoicemailDeletedEvent(
            self.voicemail.id, self.voicemail.tenant_uuid
        )

        self.notifier.deleted(self.voicemail)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_voicemail_deleted_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload']}
        self.notifier.deleted(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
