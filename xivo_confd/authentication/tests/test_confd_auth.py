# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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
import requests
import unittest

from flask import Flask
from hamcrest import assert_that, equal_to
from mock import patch
from xivo_confd.authentication.confd_auth import ConfdAuth


class TestConfdAuthBase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)

        self.app.config['auth'] = {'host': 'localhost',
                                   'port': 9497}
        self.auth = ConfdAuth()

        @self.app.route('/')
        @self.auth.login_required
        def action():
            return 'called'

        self.client = self.app.test_client()


@patch('xivo_dao.accesswebservice_dao.get_allowed_hosts')
class TestConfdAuthAllowedHosts(TestConfdAuthBase):

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


class TestConfdAuthCredentials(TestConfdAuthBase):

    def setUp(self):
        patch('xivo_dao.accesswebservice_dao.get_allowed_hosts', return_value=[]).start()
        patch('xivo_dao.accesswebservice_dao.get_password').start()
        super(TestConfdAuthCredentials, self).setUp()

    def tearDown(self):
        patch.stopall()

    def test_when_request_not_from_allowed_host_then_returns_401(self):
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))

    def test_when_request_authenticated_then_calls_action(self):
        auth = 'Digest username="username",realm="realm",nonce="nonce",uri="/",response="response",opaque="opaque"'

        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        with patch.object(self.auth, 'authenticate') as mock_auth:
            mock_auth.return_value = True
            response = self.client.get('/',
                                       environ_base={'REMOTE_ADDR': '192.168.0.1'},
                                       headers={'Authorization': auth})

            assert_that(mock_auth.call_count, equal_to(1))
            assert_that(response.status_code, equal_to(200))
            assert_that(response.data, equal_to('called'))


class TestConfdAuthToken(TestConfdAuthBase):

    def setUp(self):
        patch('xivo_dao.accesswebservice_dao.get_allowed_hosts', return_value=[]).start()
        patch('xivo_dao.accesswebservice_dao.get_password').start()
        self.auth_client = patch('xivo_confd.authentication.confd_auth.AuthClient').start().return_value
        self.auth_client.token.is_valid.side_effect = (lambda token, required_acl=None: token == 'valid-token')
        super(TestConfdAuthToken, self).setUp()

    def tearDown(self):
        patch.stopall()

    def test_when_request_with_no_token_then_returns_401(self):
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))

    def test_when_request_with_unreachable_auth_server_then_returns_401(self):
        self.auth_client.token.is_valid.side_effect = requests.RequestException
        response = self.client.get('/',
                                   environ_base={'REMOTE_ADDR': '192.168.0.1'},
                                   headers={'X-Auth-Token': 'valid-token'})

        assert_that(response.status_code, equal_to(401))

    def test_when_request_with_invalid_token_then_returns_401(self):
        response = self.client.get('/',
                                   environ_base={'REMOTE_ADDR': '192.168.0.1'},
                                   headers={'X-Auth-Token': 'invalid-token'})

        assert_that(response.status_code, equal_to(401))

    def test_when_request_with_valid_token_then_calls_action(self):
        response = self.client.get('/',
                                   environ_base={'REMOTE_ADDR': '192.168.0.1'},
                                   headers={'X-Auth-Token': 'valid-token'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))
