# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013 Avencall
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
from xivo_restapi import flask_http_server


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        flask_http_server.register_blueprints_v1_0()
        flask_http_server.app.testing = True
        flask_http_server.app.config['SERVER_NAME'] = None
        cls.app = flask_http_server.app.test_client()
