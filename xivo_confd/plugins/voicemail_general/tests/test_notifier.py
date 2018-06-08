# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.voicemail_general.event import EditVoicemailGeneralEvent
from xivo_dao.alchemy.staticvoicemail import StaticVoicemail

from ..notifier import VoicemailGeneralNotifier

SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['voicemail reload'],
                     'agentbus': []}


class TestVoicemailGeneralNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.voicemail_general = Mock(StaticVoicemail)
        self.sysconfd = Mock()

        self.notifier = VoicemailGeneralNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_general_edited_then_event_sent_on_bus(self):
        expected_event = EditVoicemailGeneralEvent()

        self.notifier.edited(self.voicemail_general)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_voicemail_general_edited_then_voicemail_reloaded(self):
        self.notifier.edited(self.voicemail_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
