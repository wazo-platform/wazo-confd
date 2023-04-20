# Copyright 2021-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, has_entries

from ..schema import CustomDestinationSchema, ForwardDestinationSchema


class TestCustomDestinationSchema(unittest.TestCase):
    def test_trailing_nbsp(self):
        exten = '123' + '\xa0'
        schema = CustomDestinationSchema()
        body = {'exten': exten, 'type': 'custom'}

        result = schema.load(body)

        assert_that(result, has_entries(exten='123'))

    def test_trailing_new_line(self):
        exten = '123\n'
        schema = CustomDestinationSchema()
        body = {'exten': exten, 'type': 'custom'}

        result = schema.load(body)

        assert_that(result, has_entries(exten='123'))


class TestForwardDestinationSchema(unittest.TestCase):
    def test_trailing_nbsp(self):
        exten = '123' + '\xa0'
        schema = ForwardDestinationSchema()
        body = {'exten': exten, 'type': 'forward', 'forward': 'busy'}

        result = schema.load(body)

        assert_that(result, has_entries(exten='123'))

    def test_trailing_new_line(self):
        exten = '123\n'
        schema = ForwardDestinationSchema()
        body = {'exten': exten, 'type': 'forward', 'forward': 'busy'}

        result = schema.load(body)

        assert_that(result, has_entries(exten='123'))
