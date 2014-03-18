# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import flask
import unittest

from flask import session
from flask.app import Flask
from mock import Mock
from xivo_dao import accesswebservice_dao
from xivo_restapi.authentication.xivo_realm_digest import XivoRealmDigest


class TestXivoRealmDigest(unittest.TestCase):

    def setUp(self):
        self.realmDigest = XivoRealmDigest('xivotestdigest')
        self.app = Flask(__name__)
        self.app.secret_key = 'test'
        self.template_authorization_header = 'Digest username="%s",' + \
                                             'realm="a",' + \
                                             'nonce="a",' + \
                                             'uri="a",' + \
                                             'response="a"'

    def test_authentication_needed(self):
        ctx = self.app.test_request_context('/users/', environ_base={'REMOTE_ADDR': '132.52.61.4'})
        ctx.push()

        self.realmDigest.challenge = Mock()
        self.realmDigest.challenge.return_value = 'this is a challenge'

        service_function = Mock()
        service_function.__name__ = 'get all campaigns'

        self.realmDigest.isRemoteAddressAllowed = Mock()
        self.realmDigest.isRemoteAddressAllowed.return_value = False

        decorated_function = self.realmDigest.requires_auth(service_function)
        challenge = decorated_function('arg1', 2, None)
        self.assertEquals(challenge, 'this is a challenge')
        self.realmDigest.challenge.assert_called_once_with()

    def test_not_needed_for_this_ip(self):
        ctx = self.app.test_request_context('/users/', base_url='http://127.0.0.1/', environ_base={'REMOTE_ADDR': '127.0.0.1'})
        ctx.push()
        service_function = Mock()
        service_function.__name__ = 'get all campaigns'

        self.realmDigest.isRemoteAddressAllowed = Mock()
        self.realmDigest.isRemoteAddressAllowed.return_value = True

        decorated_function = self.realmDigest.requires_auth(service_function)
        decorated_function('arg1', 2, None)
        self.realmDigest.isRemoteAddressAllowed.assert_called_once_with("127.0.0.1")
        service_function.assert_called_once_with('arg1', 2, None)

    def test_client_authenticates(self):
        ctx = self.app.test_request_context('/users/',
                                            base_url='http://127.0.0.1/',
                                            environ_base={'REMOTE_ADDR': 'njnjj',
                                                          'HTTP_AUTHORIZATION': self.template_authorization_header % 'test_user'})
        ctx.push()
        service_function = Mock()
        service_function.__name__ = 'get all campaigns'
        self.realmDigest.isRemoteAddressAllowed = Mock()
        self.realmDigest.isRemoteAddressAllowed.return_value = False
        self.realmDigest.isSessionLogged = Mock()
        self.realmDigest.isSessionLogged.return_value = False
        self.realmDigest.isAuthenticated = Mock()
        self.realmDigest.isAuthenticated.return_value = True
        decorated_function = self.realmDigest.requires_auth(service_function)

        decorated_function('arg1', 2, None)
        self.realmDigest.isAuthenticated.assert_called_with(flask.request)
        service_function.assert_called_with('arg1', 2, None)

    def test_client_with_session(self):
        self.realmDigest.isSessionLogged = Mock()
        self.realmDigest.isSessionLogged.return_value = True
        service_function = Mock()
        service_function.__name__ = 'get all campaigns'
        self.realmDigest.isRemoteAddressAllowed = Mock()
        self.realmDigest.isRemoteAddressAllowed.return_value = False

        decorated_function = self.realmDigest.requires_auth(service_function)
        decorated_function('arg1', 2, None)
        service_function.assert_called_once_with('arg1', 2, None)

    def test_logged_after_authentication(self):
        ctx = self.app.test_request_context('/users/',
                                            base_url='http://127.0.0.1/',
                                            environ_base={'HTTP_AUTHORIZATION': self.template_authorization_header % 'test_user'})
        ctx.push()
        self.realmDigest.isSessionLogged = Mock()
        self.realmDigest.isSessionLogged.return_value = False
        service_function = Mock()
        service_function.__name__ = 'get all campaigns'
        self.realmDigest.isRemoteAddressAllowed = Mock()
        self.realmDigest.isRemoteAddressAllowed.return_value = False
        self.realmDigest.isAuthenticated = Mock()
        self.realmDigest.isAuthenticated.return_value = True

        decorated_function = self.realmDigest.requires_auth(service_function)
        decorated_function('arg1', 2, None)
        service_function.assert_called_once_with('arg1', 2, None)
        self.assertTrue('logged' in session)
        self.assertTrue(session['logged'])
        self.assertTrue('username' in session)
        self.assertTrue(session['username'], 'test_user')

    def test_session_not_logged(self):
        session = {}
        self.assertFalse(self.realmDigest.isSessionLogged(session))

    def test_session_logged(self):
        session = {'logged': True}
        self.assertTrue(self.realmDigest.isSessionLogged(session))

    def test_localhost_is_allowed(self):
        self.assertTrue(self.realmDigest.isRemoteAddressAllowed('127.0.0.1'))

    def test_known_ip_address(self):
        accesswebservice_dao.get_allowed_hosts = Mock()
        accesswebservice_dao.get_allowed_hosts.return_value = ['12.13.14.15']
        self.assertTrue(self.realmDigest.isRemoteAddressAllowed('12.13.14.15'))
        self.assertFalse(self.realmDigest.isRemoteAddressAllowed('12.13.14.12'))
