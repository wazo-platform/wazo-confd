# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from flask import Flask
from werkzeug.exceptions import HTTPException, BadRequest

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import ServiceError

from ..common import handle_api_exception


class TestCommon(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = Flask('test')
        app.testing = True
        app.test_request_context('').push()

    def assertResponse(self, response, expected_code, result):
        data, status_code = response

        self.assertEqual(status_code, expected_code)
        self.assertEqual(data, result)


class TestHandleError(TestCommon):

    def raise_(self, ex):
        raise ex

    def test_when_not_found_error_is_raised(self):
        expected_status_code = 404
        expected_message = ["not found error"]
        exception = NotFoundError("not found error")

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_service_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["service error"]
        exception = ServiceError("service error")

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_bad_request_is_raised(self):
        expected_status_code = 400
        expected_message = ["bad request"]
        exception = BadRequest("bad request")

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_flask_restful_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["Input Error - field: missing"]

        exception = HTTPException()
        exception.data = {'message': {'field': 'missing'}}
        exception.code = 400

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_generic_http_error_is_raised(self):
        expected_status_code = 400
        expected_message = ["generic http error"]

        exception = HTTPException("generic http error")
        exception.code = 400

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)

    def test_when_generic_exception_is_raised_unicode(self):
        expected_status_code = 500
        expected_message = ["Unexpected error: error message. not ascii: é"]
        exception = Exception("error message. not ascii: é")

        response = handle_api_exception(lambda: self.raise_(exception))()

        self.assertResponse(response, expected_status_code, expected_message)
