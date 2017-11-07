# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import Mock

from xivo_bus.resources.voicemail_zonemessages.event import EditVoicemailZoneMessagesEvent

from xivo_confd.plugins.voicemail_zonemessages.notifier import VoicemailZoneMessagesNotifier

from xivo_dao.alchemy.staticvoicemail import StaticVoicemail

SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['voicemail reload'],
                     'agentbus': []}


class TestVoicemailZoneMessagesNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.voicemail_zonemessages = Mock(StaticVoicemail)
        self.sysconfd = Mock()

        self.notifier = VoicemailZoneMessagesNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_zonemessages_edited_then_event_sent_on_bus(self):
        expected_event = EditVoicemailZoneMessagesEvent()

        self.notifier.edited(self.voicemail_zonemessages)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_voicemail_zonemessages_edited_then_voicemail_reloaded(self):
        self.notifier.edited(self.voicemail_zonemessages)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
