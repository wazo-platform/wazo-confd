# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import patch, Mock

from xivo_dao.alchemy.user_line import UserLine
from xivo_confd.plugins.user_line import notifier


class TestUserLineNotifier(unittest.TestCase):

    @patch('xivo_confd.plugins.user_line.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_line.notifier.bus_event_associated')
    def test_associated(self, bus_event_associated, sysconf_command_association_updated):
        user_line = UserLine(user_id=1, line_id=2, main_user=True, main_line=True)

        notifier.associated(user_line)

        sysconf_command_association_updated.assert_called_once_with(user_line)
        bus_event_associated.assert_called_once_with(user_line)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    def test_send_sysconf_command_association_updated(self, exec_request_handlers):
        user_line = UserLine(user_id=1, line_id=2, main_user=True, main_line=True)

        expected_sysconf_command = {
            'ctibus': [],
            'ipbx': ['dialplan reload', 'sip reload'],
            'agentbus': []
        }

        notifier.sysconf_command_association_updated(user_line)

        exec_request_handlers.assert_called_once_with(expected_sysconf_command)

    @patch('xivo_bus.resources.user_line.event.UserLineAssociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_associated(self, send_bus_event, UserLineAssociatedEvent):
        new_event = UserLineAssociatedEvent.return_value = Mock()

        user_line = UserLine(user_id=1, line_id=2, main_user=True, main_line=True)

        notifier.bus_event_associated(user_line)

        UserLineAssociatedEvent.assert_called_once_with(user_line.user_id,
                                                        user_line.line_id,
                                                        True,
                                                        True)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_confd.plugins.user_line.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_line.notifier.bus_event_dissociated')
    def test_dissociated(self, bus_event_dissociated, sysconf_command_association_updated):
        user_line = UserLine(user_id=1, line_id=2, main_user=True, main_line=True)

        notifier.dissociated(user_line)

        sysconf_command_association_updated.assert_called_once_with(user_line)
        bus_event_dissociated.assert_called_once_with(user_line)

    @patch('xivo_bus.resources.user_line.event.UserLineDissociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_dissociated(self, send_bus_event, UserLineDissociatedEvent):
        new_event = UserLineDissociatedEvent.return_value = Mock()

        user_line = UserLine(user_id=1, line_id=2, main_user=True, main_line=True)

        notifier.bus_event_dissociated(user_line)

        UserLineDissociatedEvent.assert_called_once_with(user_line.user_id,
                                                         user_line.line_id,
                                                         True,
                                                         True)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
