# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+


import unittest
from hamcrest import assert_that, contains
from mock import call, patch, Mock

from xivo_dao.alchemy.voicemail import Voicemail

from xivo_bus.resources.voicemail.event import (CreateVoicemailEvent,
                                                DeleteVoicemailEvent,
                                                EditVoicemailEvent,
                                                EditUserVoicemailEvent)

from xivo_confd.plugins.voicemail.notifier import VoicemailNotifier


class TestVoicemailNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.voicemail = Mock(Voicemail, id=10, users=[])
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
        user = Mock(uuid='abc-123')
        self.voicemail.users = [user]
        expected_event1 = EditVoicemailEvent(self.voicemail.id)
        expected_event2 = EditUserVoicemailEvent(user.uuid, self.voicemail.id)

        self.notifier.edited(self.voicemail)

        assert_that(self.bus.send_bus_event.call_args_list,
                    contains(call(expected_event1, expected_event1.routing_key),
                             call(expected_event2, expected_event2.routing_key)))

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
