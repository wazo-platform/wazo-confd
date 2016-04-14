# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import Mock

from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean


class TestStrictBolean(unittest.TestCase):

    def test_that_strict_boolean_raise_error(self):
        strict = StrictBoolean()._deserialize
        self.assertRaises(ValidationError, strict, '1', None, None)

    def test_that_strict_boolean_pass(self):
        strict = StrictBoolean()._deserialize
        self.assertEqual(strict(True, None, None), True)


class TestBaseSchema(unittest.TestCase):

    def test_that_handle_error_format_message_in_string(self):
        error = Mock()
        error.message = {'key1': ['key1_error1', 'key1_error2'],
                         'key2': ['key2_error1']}
        expected_error = {'key1': 'key1_error1',
                          'key2': 'key2_error1'}
        with self.assertRaises(BadRequest) as err:
            BaseSchema().handle_error(error, None)

        self.assertEqual(err.exception.data['message'], expected_error)
