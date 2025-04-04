# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from wazo_bus.resources.user_voicemail.event import (
    UserVoicemailAssociatedEvent,
    UserVoicemailDissociatedEvent,
)

from ..notifier import UserVoicemailNotifier

USER_ID = 1
USER_LINE1_ID = 11
USER_LINE2_ID = 12
TENANT_UUID = str(uuid4())

EXPECTED_SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
}


class TestUserVoicemailNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.user = Mock(
            uuid='1234-abcd',
            id=1,
            lines=[Mock(id=USER_LINE1_ID), Mock(id=USER_LINE2_ID)],
            tenant_uuid=TENANT_UUID,
        )
        self.voicemail = Mock(id=2)

        self.notifier = UserVoicemailNotifier(self.bus, self.sysconfd)

    def test_associated_then_bus_event(self):
        expected_event = UserVoicemailAssociatedEvent(
            self.voicemail.id, self.user.tenant_uuid, self.user.uuid
        )

        self.notifier.associated(self.user, self.voicemail)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associated_then_sip_reload(self):
        self.notifier.associated(self.user, self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )

    def test_dissociated_then_bus_event(self):
        expected_event = UserVoicemailDissociatedEvent(
            self.voicemail.id, self.user.tenant_uuid, self.user.uuid
        )

        self.notifier.dissociated(self.user, self.voicemail)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociated_then_sip_reload(self):
        self.notifier.dissociated(self.user, self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )
