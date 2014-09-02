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
from hamcrest import assert_that, contains

from xivo_confd import flask_http_server as server


class TestLoadResources(unittest.TestCase):

    @patch('xivo_confd.flask_http_server._list_resources')
    @patch('xivo_confd.flask_http_server._load_module')
    def test_load_resources(self, load_module, list_resources):
        list_resources.return_value = ['resource1', 'resource2']

        server._load_resources()

        load_module.assert_any_call('xivo_confd.resources.resource1.routes')
        load_module.assert_any_call('xivo_confd.resources.resource2.routes')


class TestListResources(unittest.TestCase):

    @patch('pkg_resources.resource_listdir')
    def test_given_no_files_then_returns_empty_list(self, resource_listdir):
        resource_listdir.return_value = []

        result = server._list_resources()

        assert_that(result, contains())

    @patch('pkg_resources.resource_listdir')
    def test_given_python_files_then_returns_empty_list(self, resource_listdir):
        resource_listdir.return_value = ['python_file.py', 'python_file.pyc']

        result = server._list_resources()

        assert_that(result, contains())

    @patch('pkg_resources.resource_isdir')
    @patch('pkg_resources.resource_listdir')
    def test_given_directory_then_returns_list_with_directory_name(self, resource_listdir, resource_isdir):
        resource_listdir.return_value = ['directory']
        resource_isdir.return_value = True

        result = server._list_resources()

        assert_that(result, contains('directory'))

    @patch('pkg_resources.resource_isdir')
    @patch('pkg_resources.resource_listdir')
    def test_given_file_then_returns_empty_list(self, resource_listdir, resource_isdir):
        resource_listdir.return_value = ['file']
        resource_isdir.return_value = False

        result = server._list_resources()

        assert_that(result, contains())

    @patch('pkg_resources.resource_listdir')
    def test_given_import_error_then_returns_empty_list(self, resource_listdir):
        resource_listdir.side_effect = ImportError

        result = server._list_resources()

        assert_that(result, contains())


class TestLoadModule(unittest.TestCase):

    @patch.object(server, 'app')
    @patch('__builtin__.__import__')
    def test_given_module_name_then_registers_blueprints(self, import_, app):
        package = import_.return_value = Mock()
        module = package.module = Mock()

        server._load_module('package.module')

        import_.assert_any_call('package.module')
        module.register_blueprints.assert_called_once_with(app)

    @patch('__builtin__.__import__')
    def test_given_import_error_then_does_not_raise_error(self, import_):
        import_.side_effect = ImportError

        server._load_module('package.module')

        import_.assert_any_call('package.module')
