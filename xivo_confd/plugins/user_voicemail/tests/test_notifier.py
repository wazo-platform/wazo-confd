# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import patch, Mock

from xivo_confd.plugins.user_voicemail import notifier


class TestUserVoicemailNotifier(unittest.TestCase):

    def setUp(self):
        self.user = Mock(id=1, uuid='1234-abc', lines=[])
        self.voicemail = Mock(id=2)

    @patch('xivo_confd.plugins.user_voicemail.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_voicemail.notifier.bus_event_associated')
    def test_associated(self, bus_event_associated, sysconf_command_association_updated):
        notifier.associated(self.user, self.voicemail)

        sysconf_command_association_updated.assert_called_once_with(self.user)
        bus_event_associated.assert_called_once_with(self.user, self.voicemail)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    def test_send_sysconf_command_association_updated(self, exec_request_handlers):
        line_1 = Mock(id=3)
        line_2 = Mock(id=4)
        self.user.lines = [line_1, line_2]

        expected_sysconf_command = {
            'ctibus': ['xivo[user,edit,1]', 'xivo[phone,edit,3]', 'xivo[phone,edit,4]'],
            'ipbx': ['sip reload', 'module reload chan_sccp.so'],
            'agentbus': []
        }

        notifier.sysconf_command_association_updated(self.user)

        exec_request_handlers.assert_called_once_with(expected_sysconf_command)

    @patch('xivo_bus.resources.user_voicemail.event.UserVoicemailAssociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_associated(self, send_bus_event, UserVoiceailAssociatedEvent):
        new_event = UserVoiceailAssociatedEvent.return_value = Mock()

        notifier.bus_event_associated(self.user, self.voicemail)

        UserVoiceailAssociatedEvent.assert_called_once_with(self.user.uuid,
                                                            self.voicemail.id)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_confd.plugins.user_voicemail.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_voicemail.notifier.bus_event_dissociated')
    def test_dissociated(self, bus_event_dissociated, sysconf_command_association_updated):
        notifier.dissociated(self.user, self.voicemail)

        sysconf_command_association_updated.assert_called_once_with(self.user)
        bus_event_dissociated.assert_called_once_with(self.user, self.voicemail)

    @patch('xivo_bus.resources.user_voicemail.event.UserVoicemailDissociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_dissociated(self, send_bus_event, UserVoiceailDissociatedEvent):
        new_event = UserVoiceailDissociatedEvent.return_value = Mock()

        notifier.bus_event_dissociated(self.user, self.voicemail)

        UserVoiceailDissociatedEvent.assert_called_once_with(self.user.uuid,
                                                             self.voicemail.id)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
