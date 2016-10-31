# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
import json

from flask import Flask
from werkzeug.exceptions import HTTPException, BadRequest

from xivo_confd.helpers.common import handle_error
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import ServiceError


class TestCommon(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = Flask('test')
        app.testing = True
        app.test_request_context('').push()

    def assertResponse(self, response, expected_code, result):
        data, status_code, headers = response

        self.assertEquals(status_code, expected_code)
        self.assertEquals(json.loads(data), result)


class TestHandleError(TestCommon):

    def test_when_not_found_error_is_raised(self):
        expected_status_code = 404
        expected_message = ["not found error"]
        exception = NotFoundError("not found error")

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_service_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["service error"]
        exception = ServiceError("service error")

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_bad_request_is_raised(self):
        expected_status_code = 400
        expected_message = ["bad request"]
        exception = BadRequest("bad request")

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_flask_restful_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["Input Error - field: missing"]

        exception = HTTPException()
        exception.data = {'message': {'field': 'missing'}}
        exception.code = 400

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_generic_http_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["generic http error"]

        exception = HTTPException("generic http error")
        exception.code = 400

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_generic_exception_is_raised_str(self):
        expected_status_code = 500
        expected_message = [u"Unexpected error: error message. not ascii: é, not utf-8: \ufffd"]
        exception = Exception("error message. not ascii: é, not utf-8: \xc9")

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_generic_exception_is_raised_unicode(self):
        expected_status_code = 500
        expected_message = [u"Unexpected error: error message. not ascii: é"]
        exception = Exception(u"error message. not ascii: é")

        response = handle_error(exception)

        self.assertResponse(response, expected_status_code, expected_message)
