# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from unittest import TestCase

from hamcrest import (
    assert_that,
    equal_to,
    has_entry,
)

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
