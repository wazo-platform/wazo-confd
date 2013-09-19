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
from mock import patch
from xivo_restapi import flask_http_server
from xivo_restapi.authentication import xivo_realm_digest
from xivo_restapi.helpers import serializer
from xivo_restapi.negotiate import flask_negotiate


class TestResources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._patch_decorators()
        cls._mock_decorators()
        flask_http_server.register_blueprints_v1_1()
        flask_http_server.app.testing = True
        cls.app = flask_http_server.app.test_client()

    @classmethod
    def _patch_decorators(cls):
        cls.requires_auth_patcher = patch.object(xivo_realm_digest.realmDigest, 'requires_auth')
        cls.consumes_patcher = patch.object(flask_negotiate, 'produces')
        cls.produces_patcher = patch.object(flask_negotiate, 'consumes')

        cls.requires_auth = cls.requires_auth_patcher.start()
        cls.consumes = cls.consumes_patcher.start()
        cls.produces = cls.produces_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.requires_auth_patcher.stop()
        cls.consumes_patcher.stop()
        cls.produces_patcher.stop()

    @classmethod
    def _mock_decorators(cls):
        def mock_basic_decorator(func):
            return func

        def mock_parameterized_decorator(*decorator_args, **decorator_kwargs):
            def decorated(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper
            return decorated

        cls.requires_auth.side_effect = mock_basic_decorator
        cls.consumes.side_effect = mock_parameterized_decorator
        cls.produces.side_effect = mock_parameterized_decorator

    def _serialize_encode(self, data):
        return serializer.encode(data)

    def _serialize_decode(self, data):
        return serializer.decode(data)
