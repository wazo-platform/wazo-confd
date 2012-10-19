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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


import unittest
from mock import Mock
from xivo_recording.http_server import HttpServer


class TestHttpServer(unittest.TestCase):

    def setUp(self):
        self.http_server = HttpServer(5999)

    def test_create_named_campaign_monoqueue(self):
        response = Mock()

        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json')
        ]

        response.assert_called_with(status, headers)
