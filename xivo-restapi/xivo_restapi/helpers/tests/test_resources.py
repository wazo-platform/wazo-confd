# -*- coding: UTF-8 -*-

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

from functools import wraps
from mock import Mock
from xivo_restapi import flask_http_server
from xivo_restapi.authentication import xivo_realm_digest
from xivo_restapi.helpers import serializer
from xivo_restapi.negotiate import flask_negotiate


class TestResources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._mock_decorators()
        flask_http_server.register_blueprints_v1_1()
        flask_http_server.app.testing = True
        cls.app = flask_http_server.app.test_client()

    @classmethod
    def _mock_decorators(cls):
        def mock_basic_decorator(func):
            return func

        def mock_parameterized_decorator(string, **decorator_kwargs):
            def decorated(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper
            return decorated

        xivo_realm_digest.realmDigest = Mock()
        xivo_realm_digest.realmDigest.requires_auth.side_effect = mock_basic_decorator
        flask_negotiate.consumes = Mock()
        flask_negotiate.consumes.side_effect = mock_parameterized_decorator
        flask_negotiate.produces = Mock()
        flask_negotiate.produces.side_effect = mock_parameterized_decorator

    def _serialize_encode(self, data):
        return serializer.encode(data)

    def _serialize_decode(self, data):
        return serializer.decode(data)
