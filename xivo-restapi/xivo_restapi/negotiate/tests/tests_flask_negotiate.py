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

import unittest

from flask.app import Flask
from flask.helpers import make_response
from werkzeug.exceptions import UnsupportedMediaType, NotAcceptable
from xivo_restapi.negotiate.flask_negotiate import consumes, produces


class TestNegotiate(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'

    def _mock_headers(self, headers={}, **kwargs):
        ctx = self.app.test_request_context('', headers=headers, **kwargs)
        ctx.push()


class TestConsumes(TestNegotiate):

    def test_consumes_accepted(self):
        self._mock_headers(content_type='application/json')
        status_code = 200

        @consumes("application/json")
        def decorated_func():
            return make_response('', status_code)

        result = decorated_func()
        self.assertEqual(status_code, result.status_code)

    def test_consumes_rejected(self):
        self._mock_headers(content_type='application/json')
        status_code = 200

        @consumes("application/xml")
        def decorated_func():
            return make_response('', status_code)

        self.assertRaises(UnsupportedMediaType, decorated_func)

    def test_consumes_no_content_type(self):
        self._mock_headers()
        status_code = 200

        @consumes("application/xml")
        def decorated_func():
            return make_response('', status_code)

        self.assertRaises(UnsupportedMediaType, decorated_func)


class TestProduces(TestNegotiate):

    def test_produces_accepted(self):
        self._mock_headers({'Accept': 'application/json'})
        status_code = 200

        @produces("application/json")
        def decorated_func():
            return make_response('', status_code)

        result = decorated_func()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals("application/json", result.content_type)

    def test_produces_accepted_explicit_response_content_type(self):
        self._mock_headers({'Accept': 'text/csv'})
        status_code = 200

        @produces("text/csv", response_content_type='text/csv; charset=utf8')
        def decorated_func():
            return make_response('', status_code)

        result = decorated_func()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals("text/csv; charset=utf8", result.content_type)

    def test_produces_rejected(self):
        self._mock_headers({'Accept': 'application/json'})
        status_code = 200

        @produces("application/xml")
        def decorated_func():
            return make_response('', status_code)

        self.assertRaises(NotAcceptable, decorated_func)

    def test_produces_empty_header(self):
        self._mock_headers()
        status_code = 200

        @produces("application/json")
        def decorated_func():
            return make_response('', status_code)

        result = decorated_func()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals("application/json", result.content_type)

    def test_produces_accept_all(self):
        self._mock_headers({'Accept': '*/*'})
        status_code = 200

        @produces("application/json")
        def decorated_func():
            return make_response('', status_code)

        result = decorated_func()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals("application/json", result.content_type)
