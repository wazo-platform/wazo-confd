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

from datetime import datetime
from xivo_restapi.rest.helpers import global_helper
from xivo_restapi.rest.helpers.global_helper import str_to_datetime
from xivo_restapi.services.utils.exceptions import InvalidInputException
import unittest


class TestGlobalHelper(unittest.TestCase):

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
