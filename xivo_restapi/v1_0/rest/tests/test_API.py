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
from xivo_restapi.v1_0.rest import routing


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls, module_name):
        route = getattr(routing, '_%s_routes' % module_name)
        route()
        routes_service = getattr(routing, '%ss_service' % module_name)
        flask_http_server.app.register_blueprint(routes_service)

        flask_http_server.app.config['TESTING'] = True
        flask_http_server.app.config['SERVER_NAME'] = None
        cls.app = flask_http_server.app.test_client()
