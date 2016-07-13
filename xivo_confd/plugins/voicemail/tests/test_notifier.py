# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.resources.voicemail.model import Voicemail

from xivo_bus.resources.voicemail.event import (CreateVoicemailEvent,
                                                DeleteVoicemailEvent,
                                                EditVoicemailEvent)

from xivo_confd.plugins.voicemail.notifier import VoicemailNotifier


class TestVoicemailNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.voicemail = Mock(Voicemail, id=10)
        self.notifier = VoicemailNotifier(self.bus, self.sysconfd)

    def test_when_voicemail_created_then_event_sent_on_bus(self):
        expected_event = CreateVoicemailEvent(self.voicemail.id)

        self.notifier.created(self.voicemail)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_voicemail_created_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload'],
                             'agentbus': [],
                             'ctibus': ['xivo[voicemail,add,{}]'.format(self.voicemail.id)]}
        self.notifier.created(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_edited_then_event_sent_on_bus(self):
        expected_event = EditVoicemailEvent(self.voicemail.id)

        self.notifier.edited(self.voicemail)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_voicemail_edited_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload', 'sip reload', 'module reload chan_sccp.so'],
                             'agentbus': [],
                             'ctibus': ['xivo[voicemail,edit,{}]'.format(self.voicemail.id)]}
        self.notifier.edited(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_voicemail_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteVoicemailEvent(self.voicemail.id)

        self.notifier.deleted(self.voicemail)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_voicemail_deleted_then_sysconfd_called(self):
        expected_handlers = {'ipbx': ['voicemail reload'],
                             'agentbus': [],
                             'ctibus': ['xivo[voicemail,delete,{}]'.format(self.voicemail.id)]}
        self.notifier.deleted(self.voicemail)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)
