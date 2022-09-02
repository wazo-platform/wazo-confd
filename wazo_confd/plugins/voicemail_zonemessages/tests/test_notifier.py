# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from xivo_bus.resources.voicemail_zonemessages.event import (
    VoicemailZoneMessagesEditedEvent,
)
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail

from ..notifier import VoicemailZoneMessagesNotifier

SYSCONFD_HANDLERS = {'ipbx': ['voicemail reload']}


class TestVoicemailZoneMessagesNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.voicemail_zonemessages = Mock(StaticVoicemail)
        self.sysconfd = Mock()

        self.notifier = VoicemailZoneMessagesNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_zonemessages_edited_then_event_sent_on_bus(self):
        expected_event = VoicemailZoneMessagesEditedEvent()

        self.notifier.edited(self.voicemail_zonemessages)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_voicemail_zonemessages_edited_then_voicemail_reloaded(self):
        self.notifier.edited(self.voicemail_zonemessages)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
