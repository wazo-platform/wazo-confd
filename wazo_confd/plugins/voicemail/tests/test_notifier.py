# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, contains
from uuid import uuid4
from mock import call, Mock

from xivo_dao.alchemy.voicemail import Voicemail

from xivo_bus.resources.voicemail.event import (
    CreateVoicemailEvent,
    DeleteVoicemailEvent,
    EditUserVoicemailEvent,
    EditVoicemailEvent,
)

from ..notifier import VoicemailNotifier


class TestVoicemailNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.voicemail = Mock(Voicemail, id=10, users=[], tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.voicemail.tenant_uuid}
        self.notifier = VoicemailNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_created_then_event_sent_on_bus(self):
        expected_event = CreateVoicemailEvent(self.voicemail.id)

        self.notifier.created(self.voicemail)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_voicemail_created_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload'], 'agentbus': []}
        self.notifier.created(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_edited_then_event_sent_on_bus(self):
        user = Mock(uuid='abc-123')
        self.voicemail.users = [user]
        expected_event1 = EditVoicemailEvent(self.voicemail.id)
        expected_event2 = EditUserVoicemailEvent(user.uuid, self.voicemail.id)

        self.notifier.edited(self.voicemail)

        assert_that(
            self.bus.send_bus_event.call_args_list,
            contains(
                call(expected_event1, headers=self.expected_headers),
                call(expected_event2, headers=self.expected_headers),
            ),
        )

    def test_when_voicemail_edited_then_sysconfd_called(self):
        expected_handlers = {
            'ipbx': [
                'voicemail reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
            ],
            'agentbus': [],
        }
        self.notifier.edited(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteVoicemailEvent(self.voicemail.id)

        self.notifier.deleted(self.voicemail)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_voicemail_deleted_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload'], 'agentbus': []}
        self.notifier.deleted(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
