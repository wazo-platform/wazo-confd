# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import os
import requests
import unittest


from mock import Mock
from flask import Flask
from hamcrest import assert_that, equal_to
from mock import patch
from xivo_confd.authentication.confd_auth import ConfdAuth
from xivo.auth_verifier import AuthVerifier


class TestConfdAuthBase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)

        config = {'auth': {'host': 'localhost',
                           'port': 9497},
                  'rest_api': {'http': {'port': 9487}}}
        self.auth = ConfdAuth()
        self.auth.set_config(config)

        @self.app.route('/')
        @self.auth.login_required
        def action():
            return 'called'

        self.client = self.app.test_client()


@patch('xivo_dao.accesswebservice_dao.get_allowed_hosts')
class TestConfdAuthAllowedHosts(TestConfdAuthBase):

    def test_when_request_from_local_host_and_local_port_then_calls_action(self, get_allowed_hosts):
        get_allowed_hosts.return_value = []

        response = self.client.get('/', environ_overrides={'REMOTE_ADDR': '127.0.0.1', 'SERVER_PORT': '9487'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))

    def test_when_request_from_allowed_host_then_calls_action(self, get_allowed_hosts):
        get_allowed_hosts.return_value = ['192.168.0.1']

        response = self.client.get('/', environ_overrides={'REMOTE_ADDR': '192.168.0.1', 'SERVER_PORT': '9486'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))

    def test_when_request_from_local_host_and_remote_port_then_request_refused(self, get_allowed_hosts):
        get_allowed_hosts.return_value = []

        response = self.client.get('/', environ_overrides={'REMOTE_ADDR': '127.0.0.1', 'SERVER_PORT': '9486'})

        assert_that(response.status_code, equal_to(401))


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
        super(TestConfdAuthToken, self).setUp()
        self.auth_verifier = Mock(AuthVerifier)
        self.auth.auth_verifier = self.auth_verifier
        self.token = self.auth_verifier.client.return_value.token
        self.auth_verifier.acl.return_value = ''

    def tearDown(self):
        patch.stopall()

    def test_when_request_with_no_token_then_returns_401(self):
        self.token.is_valid.return_value = False
        self.auth_verifier.token.return_value = ''
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))
        self.token.is_valid.assert_called_once_with('', 'confd.#')

    def test_when_request_with_unreachable_auth_server_then_returns_401(self):
        self.token.is_valid.side_effect = requests.RequestException
        self.auth_verifier.token.return_value = 'valid-token'
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))
        self.token.is_valid.assert_called_once_with('valid-token', 'confd.#')

    def test_when_request_with_invalid_token_then_returns_401(self):
        self.token.is_valid.return_value = False
        self.auth_verifier.token.return_value = 'invalid-token'
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(401))
        self.token.is_valid.assert_called_once_with('invalid-token', 'confd.#')

    def test_when_request_with_valid_token_then_calls_action(self):
        self.token.is_valid.return_value = True
        self.auth_verifier.token.return_value = 'valid-token'
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))
        self.token.is_valid.assert_called_once_with('valid-token', 'confd.#')

    def test_when_request_with_valid_token_and_acl_then_calls_action(self):
        self.auth_verifier.acl.return_value = 'confd.users.read'
        self.token.is_valid.return_value = True
        self.auth_verifier.token.return_value = 'valid-token'
        response = self.client.get('/', environ_base={'REMOTE_ADDR': '192.168.0.1'})

        assert_that(response.status_code, equal_to(200))
        assert_that(response.data, equal_to('called'))
        self.token.is_valid.assert_called_once_with('valid-token', 'confd.users.read')
