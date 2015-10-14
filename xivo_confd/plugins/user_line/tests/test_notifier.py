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

from xivo_dao.resources.user_line.model import UserLine
from xivo_confd.plugins.user_line import notifier


class TestUserLineNotifier(unittest.TestCase):

    @patch('xivo_confd.plugins.user_line.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_line.notifier.bus_event_associated')
    def test_associated(self, bus_event_associated, sysconf_command_association_updated):
        user_line = UserLine(user_id=1, line_id=2)

        notifier.associated(user_line)

        sysconf_command_association_updated.assert_called_once_with(user_line)
        bus_event_associated.assert_called_once_with(user_line)

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_send_sysconf_command_association_updated(self, find_all_by_user_id, exec_request_handlers):
        user_line = UserLine(user_id=1, line_id=2)
        user_line_1 = Mock(UserLine, line_id=3)
        user_line_2 = Mock(UserLine, line_id=4)

        find_all_by_user_id.return_value = [user_line_1, user_line_2]

        expected_sysconf_command = {
            'ctibus': ['xivo[user,edit,1]', 'xivo[phone,edit,3]', 'xivo[phone,edit,4]'],
            'dird': [],
            'ipbx': ['dialplan reload', 'sip reload'],
            'agentbus': []
        }

        notifier.sysconf_command_association_updated(user_line)

        exec_request_handlers.assert_called_once_with(expected_sysconf_command)
        find_all_by_user_id.assert_called_once_with(user_line.user_id)

    @patch('xivo_bus.resources.user_line.event.UserLineAssociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_associated(self, send_bus_event, UserLineAssociatedEvent):
        new_event = UserLineAssociatedEvent.return_value = Mock()

        user_line = UserLine(user_id=1, line_id=2)

        notifier.bus_event_associated(user_line)

        UserLineAssociatedEvent.assert_called_once_with(user_line.user_id,
                                                        user_line.line_id,
                                                        True,
                                                        True)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_confd.plugins.user_line.notifier.sysconf_command_association_updated')
    @patch('xivo_confd.plugins.user_line.notifier.bus_event_dissociated')
    def test_dissociated(self, bus_event_dissociated, sysconf_command_association_updated):
        user_line = UserLine(user_id=1, line_id=2)

        notifier.dissociated(user_line)

        sysconf_command_association_updated.assert_called_once_with(user_line)
        bus_event_dissociated.assert_called_once_with(user_line)

    @patch('xivo_bus.resources.user_line.event.UserLineDissociatedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_bus_event_dissociated(self, send_bus_event, UserLineDissociatedEvent):
        new_event = UserLineDissociatedEvent.return_value = Mock()

        user_line = UserLine(user_id=1, line_id=2)

        notifier.bus_event_dissociated(user_line)

        UserLineDissociatedEvent.assert_called_once_with(user_line.user_id,
                                                         user_line.line_id,
                                                         True,
                                                         True)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
