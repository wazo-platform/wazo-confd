# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from mock import patch, Mock

from xivo_confd import flask_http_server as server


class TestLoadResources(unittest.TestCase):

    @patch('xivo_confd.flask_http_server._load_module')
    def test_load_resources(self, load_module):
        rest_api = Mock()
        resources = ['resource1', 'resource2']

        server.register_resources(rest_api, resources)

        load_module.assert_any_call('xivo_confd.resources.resource1.actions', rest_api)
        load_module.assert_any_call('xivo_confd.resources.resource2.actions', rest_api)


class TestLoadModule(unittest.TestCase):

    @patch('__builtin__.__import__')
    def test_given_module_name_then_registers_blueprints(self, import_):
        package = import_.return_value = Mock()
        module = package.module = Mock()
        rest_api = Mock()

        server._load_module('package.module', rest_api)

        import_.assert_any_call('package.module')
        module.load.assert_called_once_with(rest_api)

    @patch('__builtin__.__import__')
    def test_given_import_error_then_does_not_raise_error(self, import_):
        import_.side_effect = ImportError
        rest_api = Mock()

        server._load_module('package.module', rest_api)

        import_.assert_any_call('package.module')
