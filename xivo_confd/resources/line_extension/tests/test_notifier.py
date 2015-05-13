# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import patch, Mock

from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.user_line.model import UserLine

from xivo_confd.resources.line_extension import notifier


class TestLineExtensionNotifier(unittest.TestCase):

    @patch('xivo_confd.resources.line_extension.notifier.send_sysconf_commands')
    @patch('xivo_confd.resources.line_extension.notifier.send_bus_association_events')
    def test_associated(self, send_bus_association_events, send_sysconf_association_commands):
        line_extension = LineExtension(line_id=1, extension_id=2)

        notifier.associated(line_extension)

        send_sysconf_association_commands.assert_called_once_with(line_extension)
        send_bus_association_events.assert_called_once_with(line_extension)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_line_id')
    def test_send_sysconf_commands(self,
                                   find_all_by_line_id,
                                   exec_request_handlers):
        line_extension = LineExtension(line_id=1, extension_id=2)
        user_line_1 = Mock(UserLine, line_id=1, user_id=3)
        user_line_2 = Mock(UserLine, line_id=1, user_id=None)

        find_all_by_line_id.return_value = [user_line_1, user_line_2]

        expected_sysconf_command = {
            'ctibus': ['xivo[phone,edit,1]', 'xivo[user,edit,3]'],
            'dird': [],
            'ipbx': ['dialplan reload', 'sip reload'],
            'agentbus': []
        }

        notifier.send_sysconf_commands(line_extension)

        exec_request_handlers.assert_called_once_with(expected_sysconf_command)
        find_all_by_line_id.assert_called_once_with(line_extension.line_id)

    @patch('xivo_bus.resources.line_extension.event.LineExtensionAssociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_send_bus_association_events(self, send_bus_event, LineExtensionAssociatedEvent):
        new_event = LineExtensionAssociatedEvent.return_value = Mock()

        line_extension = LineExtension(line_id=1, extension_id=2)

        notifier.send_bus_association_events(line_extension)

        LineExtensionAssociatedEvent.assert_called_once_with(line_extension.line_id,
                                                             line_extension.extension_id)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_confd.resources.line_extension.notifier.send_bus_dissociation_events')
    @patch('xivo_confd.resources.line_extension.notifier.send_sysconf_commands')
    def test_dissociated(self, send_sysconf_commands, send_bus_dissociation_events):
        line_extension = LineExtension(line_id=1, extension_id=2)

        notifier.dissociated(line_extension)

        send_sysconf_commands.assert_called_once_with(line_extension)
        send_bus_dissociation_events.assert_called_once_with(line_extension)

    @patch('xivo_bus.resources.line_extension.event.LineExtensionDissociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_send_bus_dissociation_events(self, send_bus_event, LineExtensionDissociatedEvent):
        new_event = LineExtensionDissociatedEvent.return_value = Mock()

        line_extension = LineExtension(line_id=1, extension_id=2)

        notifier.send_bus_dissociation_events(line_extension)

        LineExtensionDissociatedEvent.assert_called_once_with(line_extension.line_id,
                                                              line_extension.extension_id)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
