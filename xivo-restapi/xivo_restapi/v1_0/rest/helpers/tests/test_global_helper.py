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

from datetime import datetime
from flask.app import Flask
from mock import Mock
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from xivo_restapi.v1_0 import rest_encoder
from xivo_restapi.v1_0.rest.helpers import global_helper
from xivo_restapi.v1_0.rest.helpers.global_helper import str_to_datetime, \
    exception_catcher
from xivo_restapi.v1_0.services.utils.exceptions import InvalidInputException, \
    NoSuchElementException


class TestGlobalHelper(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        ctx = self.app.test_request_context('users/')
        ctx.push()

    def test_create_class_instance(self):
        class SampleClass():
            def __init__(self):
                self.att1 = 1
                self.att2 = None
                self.att3 = 'foo'

            def todict(self):
                return self.__dict__

        dict_data = {'att1': 'foo',
                     'att2': 12,
                     'att3': None,
                     'att4': 'bar'}
        expected_object = SampleClass()
        expected_object.att1 = 'foo'
        expected_object.att2 = 12
        expected_object.att3 = None

        result = global_helper.create_class_instance(SampleClass, dict_data)
        self.assertEqual(result.__dict__, expected_object.__dict__)

    def test_create_paginator_fail(self):
        data = {'param1': 1,
                'param2': 'valeur'}
        result = global_helper.create_paginator(data)
        self.assertEqual(result, (0, 0))

    def test_create_paginator_success(self):
        data = {'param1': '1',
                '_page': '2',
                '_pagesize': '20'}
        result = global_helper.create_paginator(data)
        self.assertEqual(result, (2, 20))

    def test_str_to_datetime(self):
        strDate = "2012-01-01"
        resultDate = str_to_datetime(strDate)
        self.assertEqual(resultDate, datetime.strptime(strDate, "%Y-%m-%d"))

        strTime = "2012-01-01 00:00:00"
        resultTime = str_to_datetime(strTime)
        self.assertEqual(resultTime, datetime.strptime(strTime, "%Y-%m-%d %H:%M:%S"))

        invalidDateStr = "2012-13-13"
        self.assertRaises(InvalidInputException, str_to_datetime, invalidDateStr)

        tooShortStr = '2012'
        self.assertRaises(InvalidInputException, str_to_datetime, tooShortStr)

        invalidTimeStr = '2012-01-01 00:00:99'
        self.assertRaises(InvalidInputException, str_to_datetime, invalidTimeStr)

        invalidTimeStr = None
        self.assertRaises(InvalidInputException, str_to_datetime, invalidTimeStr)

        invalidTimeStr = {}
        self.assertRaises(InvalidInputException, str_to_datetime, invalidTimeStr)

        invalidTimeStr = 2012
        self.assertRaises(InvalidInputException, str_to_datetime, invalidTimeStr)

    def test_exception_catcher_no_exception(self):
        function = Mock()
        function.return_value = 1
        decorated_function = exception_catcher(function)
        self.assertEquals(1, decorated_function("a", 1, {}))
        function.assert_called_with("a", 1, {})

    def test_exception_catcher_standard_exception(self):
        def function():
            raise Exception()
        decorated_function = exception_catcher(function)
        self.assertEquals("500 INTERNAL SERVER ERROR", decorated_function().status)

    def test_exception_catcher_HTTP_exception(self):
        def function():
            raise BadRequest()
        decorated_function = exception_catcher(function)
        self.assertRaises(HTTPException, decorated_function)

        def function2():
            raise Unauthorized()
        decorated_function = exception_catcher(function2)
        self.assertRaises(HTTPException, decorated_function)

    def test_exception_catcher_NoSuchElementException(self):
        def function():
            raise NoSuchElementException('')
        decorated_function = exception_catcher(function)
        self.assertEquals("404 NOT FOUND", decorated_function().status)

    def test_exception_catcher_ValueError(self):
        def function():
            raise ValueError()
        decorated_function = exception_catcher(function)
        result = decorated_function()
        self.assertEquals("400 BAD REQUEST", result.status)
        self.assertEquals(["No parsable data in the request"], rest_encoder.decode(result.data))
