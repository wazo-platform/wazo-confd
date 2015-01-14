# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013  Avencall
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

from flask import Flask
from flask import Response
from mock import patch
from werkzeug.exceptions import Forbidden

from xivo_confd.helpers.request_bouncer import limit_to_localhost
from xivo_confd.helpers.tests import test_resources


class TestRequestBouncer(test_resources.TestResources):

    def setUp(self):
        app = Flask('test')
        ctx = app.test_request_context('')
        ctx.push()

    @patch('xivo_confd.helpers.request_bouncer.request')
    def test_limit_to_localhost_accepted(self, request):
        request.remote_addr = '127.0.0.1'

        self.app.get('users/')

        @limit_to_localhost
        def decorated_func():
            return Response(status=200)

        result = decorated_func()
        self.assertEqual(200, result.status_code)

    @patch('xivo_confd.helpers.request_bouncer.request')
    def test_limit_to_localhost_rejected(self, request):
        request.remote_addr = '42.42.42.42'

        @limit_to_localhost
        def decorated_func():
            return Response(status=200)

        self.assertRaises(Forbidden, decorated_func)
