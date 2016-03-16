# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entry
from unittest import TestCase

from ..csv_ import output_csv

SOME_STATUS_CODE = 200
SOME_INPUT = {'headers': [], 'content': []}


class TestCSVRepresentation(TestCase):

    def test_csv_empty(self):
        result = output_csv({'headers': [], 'content': []}, SOME_STATUS_CODE)

        assert_that(result.data, equal_to('\r\n'))

    def test_csv_strings(self):
        body = [
            {'a': '1',
             'b': '2',
             'c': '3'},
            {'a': '4',
             'b': '5',
             'c': '6'},
        ]
        result = output_csv({'headers': ['a', 'b', 'c'], 'content': body}, SOME_STATUS_CODE)

        assert_that(result.data, equal_to('a,b,c\r\n1,2,3\r\n4,5,6\r\n'))

    def test_csv_non_ascii(self):
        body = [
            {'a': u'é'},
        ]
        result = output_csv({'headers': ['a'], 'content': body}, SOME_STATUS_CODE)

        assert_that(result.data, equal_to(u'a\r\né\r\n'.encode('utf-8')))

    def test_csv_integers(self):
        body = [
            {'a': 1},
        ]
        result = output_csv({'headers': ['a'], 'content': body}, SOME_STATUS_CODE)

        assert_that(result.data, equal_to('a\r\n1\r\n'))

    def test_csv_other_args(self):
        result = output_csv(SOME_INPUT, 200, {'my-header': 'my-value'})

        assert_that(result.status_code, equal_to(200))
        assert_that(result.headers, has_entry('my-header', 'my-value'))
