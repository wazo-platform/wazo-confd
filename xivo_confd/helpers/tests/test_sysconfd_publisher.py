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

import json
from mock import patch, Mock
from unittest import TestCase
from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher


class TestSysconfdClient(TestCase):

    def setUp(self):
        self.dao = Mock()
        self.url = "http://localhost:8668"
        self.client = SysconfdPublisher(self.url, self.dao)
        session_init_patch = patch('xivo_confd.helpers.sysconfd_publisher.requests.Session')
        session_init = session_init_patch.start()
        self.session = session_init.return_value
        self.addCleanup(session_init.stop)

    def test_delete_voicemail_storage(self):
        self.session.request.return_value = Mock(status_code=200)

        self.client.delete_voicemail("123", "default")
        self.client.flush()

        url = "http://localhost:8668/delete_voicemail"
        self.session.request.assert_called_once_with('GET',
                                                     url,
                                                     params={'mailbox': '123', 'context': 'default'},
                                                     data=None)

    def test_move_voicemail_storage(self):
        self.session.request.return_value = Mock(status_code=200)

        self.client.move_voicemail("100", "default", "2000", "newcontext")
        self.client.flush()

        url = "http://localhost:8668/move_voicemail"
        params = {'old_mailbox': '100',
                  'old_context': 'default',
                  'new_mailbox': '2000',
                  'new_context': 'newcontext'}
        self.session.request.assert_called_once_with('GET',
                                                     url,
                                                     params=params,
                                                     data=None)

    def test_exec_request_handlers_live_reload_enabled(self):
        self.session.request.return_value = Mock(status_code=200)
        self.dao.is_live_reload_enabled.return_value = True

        commands = {'ctibus': [],
                    'ipbx': []}

        self.client.exec_request_handlers(commands)
        self.client.flush()

        call = self.session.request.call_args_list[0]
        method = call[0][0]
        url = call[0][1]
        body = call[1]['data']

        expected_url = "http://localhost:8668/exec_request_handlers"
        self.assertEquals(method, "POST")
        self.assertEquals(url, expected_url)
        self.assertEquals(json.loads(body), commands)

        self.dao.is_live_reload_enabled.assert_called_once_with()

    def test_exec_request_handlers_live_reload_disabled(self):
        self.dao.is_live_reload_enabled.return_value = False

        commands = {'ctibus': [],
                    'ipbx': []}

        self.client.exec_request_handlers(commands)
        self.client.flush()

        self.assertFalse(self.session.request.called)
        self.dao.is_live_reload_enabled.assert_called_once_with()
