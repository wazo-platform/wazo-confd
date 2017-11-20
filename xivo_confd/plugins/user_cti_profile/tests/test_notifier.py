# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import patch, Mock

from xivo_confd.plugins.user_cti_profile import notifier


class TestUserCtiProfileNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd_command = {
            'ctibus': [],
            'ipbx': [],
            'agentbus': [],
        }

    @patch('xivo_confd.helpers.sysconfd_connector.exec_request_handlers')
    @patch('xivo_bus.resources.user_cti_profile.event.UserCtiProfileEditedEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_edited(self, send_bus_event, UserCtiProfileEditedEvent, exec_request_handler):
        new_event = UserCtiProfileEditedEvent.return_value = Mock()
        user = Mock(id=1, cti_profile_id=2, cti_enabled=True)
        self.sysconfd_command['ctibus'] = ['xivo[user,edit,1]']

        notifier.edited(user)

        UserCtiProfileEditedEvent.assert_called_once_with(user.id,
                                                          user.cti_profile_id,
                                                          user.cti_enabled)
        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
        exec_request_handler.assert_called_once_with(self.sysconfd_command)
