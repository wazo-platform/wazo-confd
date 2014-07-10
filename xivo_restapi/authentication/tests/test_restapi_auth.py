# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import os
import unittest
from hamcrest import assert_that, equal_to

from mock import patch
from flask import Flask
from xivo_restapi.authentication.restapi_auth import RestApiAuth


@patch('xivo_dao.accesswebservice_dao.get_allowed_hosts')
class TestRestApiAuth(unittest.TestCase):

    def setUp(self):
        self.app = Flask('testapp')
        self.app.secret_key = os.urandom(24)

        self.auth = RestApiAuth()

        @self.app.route('/')
        @self.auth.login_required
        def action():
            return 'called'

        self.client = self.app.test_client()

    def test_when_request_from_localhost_then_calls_action(self, get_allowed_hosts):
        get_allowed_hosts.return_value = []

        response = self.client.get('/', environ_base={'REMOTE_ADDR': '127.0.0.1'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))

    def test_when_request_from_allowed_host_then_calls_action(self, get_allowed_hosts):
        get_allowed_hosts.return_value = ['192.168.0.1']

        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))

    def test_when_request_not_from_allowed_host_then_returns_401(self, get_allowed_hosts):
        get_allowed_hosts.return_value = []

        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))

    @patch('xivo_dao.accesswebservice_dao.get_password')
    def test_when_request_authenticated_then_calls_action(self, get_password, get_allowed_hosts):
        get_allowed_hosts.return_value = []
        auth = 'Digest username="username",realm="realm",nonce="nonce",uri="/",response="response",opaque="opaque"'

        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        with patch.object(self.auth, 'authenticate') as mock_auth:
            mock_auth.return_value = True
            response = self.client.get('/',
                                       environ_base={'REMOTE_ADDR': '192.168.0.1'},
                                       headers={'Authorization': auth})

            assert_that(mock_auth.call_count, equal_to(1))
            assert_that(response.status_code, 200)
            assert_that(response.data, equal_to('called'))
