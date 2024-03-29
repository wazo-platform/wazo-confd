# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.voicemail_general.event import VoicemailGeneralEditedEvent
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail

from ..notifier import VoicemailGeneralNotifier

SYSCONFD_HANDLERS = {'ipbx': ['voicemail reload']}


class TestVoicemailGeneralNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.voicemail_general = Mock(StaticVoicemail)
        self.sysconfd = Mock()

        self.notifier = VoicemailGeneralNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_general_edited_then_event_sent_on_bus(self):
        expected_event = VoicemailGeneralEditedEvent()

        self.notifier.edited(self.voicemail_general)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_voicemail_general_edited_then_voicemail_reloaded(self):
        self.notifier.edited(self.voicemail_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
