# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from hamcrest import *
from mock import Mock, patch
from werkzeug.exceptions import HTTPException, BadRequest
from xivo_restapi.helpers.common import exception_catcher, \
    extract_find_parameters
from xivo_restapi.flask_http_server import app
from xivo_restapi.helpers import serializer

from xivo_dao.data_handler.exception import ElementNotExistsError, MissingParametersError, \
    InvalidParametersError, NonexistentParametersError, ElementAlreadyExistsError, \
    ElementCreationError, ElementEditionError, ElementDeletionError


class TestCommon(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        app.testing = True
        app.test_request_context('').push()

    def assertResponse(self, response, status_code, result):
        decoded_response = serializer.decode(response.data)

        self.assertEquals(response.status_code, status_code)
        self.assertEquals(decoded_response, result)

    def test_exception_catcher_no_exception(self):
        expected = 1
        called_with = Mock(return_value=expected)

        def function(*args, **kwargs):
            return called_with(*args, **kwargs)

        decorated_function = exception_catcher(function)

        result = decorated_function("a", 1, {})

        self.assertEquals(expected, result)
        called_with.assert_called_with("a", 1, {})

    def test_exception_catcher_value_error(self):
        expected_status_code = 400
        expected_message = ["No parsable data in the request, Be sure to send a valid JSON file"]

        def function():
            raise ValueError()

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_element_not_exists_error(self):
        expected_status_code = 404
        expected_message = ["element with id=1 does not exist"]

        def function():
            raise ElementNotExistsError('element', id=1)

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_http_exception(self):
        def function():
            raise BadRequest()

        decorated_function = exception_catcher(function)
        self.assertRaises(HTTPException, decorated_function)

    def test_exception_catcher_standard_exception(self):
        expected_status_code = 500
        expected_message = ["unexpected error during request: error message"]

        def function():
            raise Exception("error message")

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_missing_parameters_error(self):
        expected_status_code = 400
        expected_message = ["Missing parameters: parameter"]

        def function():
            raise MissingParametersError(['parameter'])

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_invalid_parameters_error(self):
        expected_status_code = 400
        expected_message = ["Invalid parameters: parameter"]

        def function():
            raise InvalidParametersError(['parameter'])

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_nonexistent_parameters_error(self):
        expected_status_code = 400
        expected_message = ["Nonexistent parameters: username johndoe does not exist"]

        def function():
            raise NonexistentParametersError(username='johndoe')

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_element_already_exists_error(self):
        expected_status_code = 400
        expected_message = ["user johndoe already exists"]

        def function():
            raise ElementAlreadyExistsError('user', 'johndoe')

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_element_creation_error(self):
        expected_status_code = 400
        expected_message = ["error while creating user: error message"]

        def function():
            raise ElementCreationError('user', 'error message')

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_element_edition_error(self):
        expected_status_code = 400
        expected_message = ["error while editing user: error message"]

        def function():
            raise ElementEditionError('user', 'error message')

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)

    def test_exception_catcher_element_deletion_error(self):
        expected_status_code = 400
        expected_message = ["error while deleting user: error message"]

        def function():
            raise ElementDeletionError('user', 'error message')

        decorated_function = exception_catcher(function)

        response = decorated_function()
        self.assertResponse(response, expected_status_code, expected_message)


class TestExtractFindParameters(unittest.TestCase):

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_invalid_skip(self, mock_request):
        mock_request.args = {
            'skip': '-532'
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, {})

        mock_request.args = {
            'skip': 'toto'
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, {})

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_skip(self, mock_request):
        expected_result = {
            'skip': 532
        }
        mock_request.args = {
            'skip': '532'
        }

        parameters = extract_find_parameters({})

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_invalid_limit(self, mock_request):
        mock_request.args = {
            'limit': '-532'
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, {})

        mock_request.args = {
            'limit': 'toto'
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, {})

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_limit(self, mock_request):
        expected_result = {
            'limit': 532
        }
        mock_request.args = {
            'limit': '532'
        }

        parameters = extract_find_parameters({})

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_direction(self, mock_request):
        expected_result = {
            'direction': 'asc'
        }
        mock_request.args = {
            'direction': 'asc'
        }

        parameters = extract_find_parameters({})

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_with_invalid_direction(self, mock_request):
        mock_request.args = {
            'direction': 'toto'
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, {})

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_search(self, mock_request):
        expected_result = {
            'search': 'abcd'
        }
        mock_request.args = {
            'search': 'abcd'
        }

        parameters = extract_find_parameters({})

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_all_args(self, mock_request):
        order_column = Mock()
        ordering = {
            'toto': order_column
        }

        expected_result = {
            'skip': 532,
            'limit': 5432,
            'order': order_column,
            'direction': 'asc',
            'search': 'abcd'
        }
        mock_request.args = {
            'skip': '532',
            'limit': '5432',
            'order': 'toto',
            'direction': 'asc',
            'search': 'abcd'
        }

        parameters = extract_find_parameters(ordering)

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_with_ordering(self, mock_request):
        order_column = Mock()

        mock_request.args = {
            'order': 'column_name'
        }

        expected_result = {
            'order': order_column
        }

        ordering = {
            'column_name': order_column
        }

        parameters = extract_find_parameters(ordering=ordering)

        assert_that(parameters, equal_to(expected_result))

    @patch('xivo_restapi.helpers.common.request')
    def test_extract_find_parameters_with_invalid_ordering(self, mock_request):
        order_column = Mock()

        mock_request.args = {
            'order': 'toto'
        }

        ordering = {
            'column_name': order_column
        }

        self.assertRaises(InvalidParametersError, extract_find_parameters, ordering)
