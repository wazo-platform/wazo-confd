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

from xivo_confd.plugins.user_cti_profile import notifier

from xivo_dao.resources.user_cti_profile.model import UserCtiProfile


class TestUserCtiProfileNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd_command = {
            'ctibus': [],
            'dird': [],
            'ipbx': [],
            'agentbus': [],
        }

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.user_cti_profile.event.UserCtiProfileEditedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_edited(self, send_bus_event, UserCtiProfileEditedEvent, exec_request_handler):
        new_event = UserCtiProfileEditedEvent.return_value = Mock()
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2, enabled=True)
        self.sysconfd_command['ctibus'] = ['xivo[user,edit,1]']

        notifier.edited(user_cti_profile)

        UserCtiProfileEditedEvent.assert_called_once_with(user_cti_profile.user_id,
                                                          user_cti_profile.cti_profile_id,
                                                          user_cti_profile.enabled)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
        exec_request_handler.assert_called_once_with(self.sysconfd_command)
