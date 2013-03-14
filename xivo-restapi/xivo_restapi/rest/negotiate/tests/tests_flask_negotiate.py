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

from flask.app import Flask
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable
from xivo_restapi.rest.negotiate.flask_negotiate import consumes, produces
import unittest


class TestFlaskNegotiate(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'

    def tearDown(self):
        self.app = None

    def test_consumes_accepted(self):
        ctx = self.app.test_request_context('users/',
                                            content_type="application/json")
        ctx.push()

        @consumes("application/json")
        def decorated_func():
            return 1

        result = decorated_func()
        self.assertEqual(1, result)

    def test_consumes_rejected(self):
        ctx = self.app.test_request_context('users/',
                                            content_type="application/json")
        ctx.push()

        @consumes("application/xml")
        def decorated_func():
            return 1

        self.assertRaises(UnsupportedMediaType, decorated_func)

    def test_produces_accepted(self):
        ctx = self.app.test_request_context('users/', headers={"Accept": "application/json"})
        ctx.push()

        @produces("application/json")
        def decorated_func():
            return 1

        self.assertEquals(1, decorated_func())

    def test_produces_rejected(self):
        ctx = self.app.test_request_context('users/', headers={"Accept": "application/json"})
        ctx.push()

        @produces("application/xml")
        def decorated_func():
            return 1

        self.assertRaises(NotAcceptable, decorated_func)

    def test_produces_empty_header(self):
        ctx = self.app.test_request_context('users/')
        ctx.push()

        @produces("application/json")
        def decorated_func():
            return 1

        self.assertEquals(1, decorated_func())

    def test_produces_accept_all(self):
        ctx = self.app.test_request_context('users/', headers={"Accept": "*/*"})
        ctx.push()

        @produces("application/json")
        def decorated_func():
            return 1

        self.assertEquals(1, decorated_func())
