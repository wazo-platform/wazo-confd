# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from mock import patch
from unittest import TestCase
from xivo_dao.helpers import sysconfd_connector


class TestSysconfdConnector(TestCase):

    @patch('xivo_dao.helpers.sysconfd_connector.sysconfd_conn_request')
    def test_delete_voicemail_storage(self, sysconfd_conn_request):
        sysconfd_connector.delete_voicemail_storage("default", "123")
        sysconfd_conn_request.assert_called_with('GET', '/delete_voicemail?context=default&name=123', '')

    @patch('xivo_dao.resources.configuration.dao.is_live_reload_enabled')
    @patch('xivo_dao.helpers.sysconfd_connector.sysconfd_conn_request')
    def test_exec_request_handlers_live_reload_enabled(self, sysconfd_conn_request, is_live_reload_enabled):
        commands = {'ctibus': [],
                    'ipbx': []}
        is_live_reload_enabled.return_value = True

        sysconfd_connector.exec_request_handlers(commands)

        sysconfd_conn_request.assert_any_call('POST', '/exec_request_handlers', commands)
        is_live_reload_enabled.assert_called_once_with()

    @patch('xivo_dao.resources.configuration.dao.is_live_reload_enabled')
    @patch('xivo_dao.helpers.sysconfd_connector.sysconfd_conn_request')
    def test_exec_request_handlers_live_reload_disabled(self, sysconfd_conn_request, is_live_reload_enabled):
        commands = {'ctibus': [],
                    'ipbx': []}
        is_live_reload_enabled.return_value = False

        sysconfd_connector.exec_request_handlers(commands)

        self.assertFalse(sysconfd_conn_request.called)
        is_live_reload_enabled.assert_called_once_with()
