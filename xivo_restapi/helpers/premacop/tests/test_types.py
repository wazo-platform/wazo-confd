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
from mock import Mock

from xivo_restapi.helpers.premacop import types
from xivo_restapi.helpers.premacop.errors import ValidationError


class TestIntFieldType(unittest.TestCase):

    def setUp(self):
        self.field_type = types.Int()

    def test_given_none_then_passes(self):
        self.field_type.validate(None)

    def test_given_wrong_type_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "'foo' is not an integer",
                                self.field_type.validate, "foo")

    def test_given_bool_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "'True' is not an integer",
                                self.field_type.validate, True)

    def test_given_int_then_passes(self):
        self.field_type.validate(1)


class TestBooleanFieldType(unittest.TestCase):

    def setUp(self):
        self.field_type = types.Boolean()

    def test_given_none_then_passes(self):
        self.field_type.validate(None)

    def test_given_wrong_type_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "'foo' is not a boolean",
                                self.field_type.validate, "foo")

    def test_given_bool_then_passes(self):
        self.field_type.validate(True)


class TestUnicodeFieldType(unittest.TestCase):

    def setUp(self):
        self.field_type = types.Unicode()

    def test_given_none_then_passes(self):
        self.field_type.validate(None)

    def test_given_wrong_type_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "'1' is not a unicode string",
                                self.field_type.validate, 1)

    def test_given_bool_then_passes(self):
        self.field_type.validate(u"foo")


class TestFloatFieldType(unittest.TestCase):

    def setUp(self):
        self.field_type = types.Float()

    def test_given_none_then_passes(self):
        self.field_type.validate(None)

    def test_given_wrong_type_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "'1' is not a floating-point number",
                                self.field_type.validate, 1)

    def test_given_bool_then_passes(self):
        self.field_type.validate(1.23)


class TestArrayFieldType(unittest.TestCase):

    def test_given_none_then_passes(self):
        field_type = types.Array(Mock())
        field_type.validate(None)

    def test_given_not_an_iterable_then_raises_error(self):
        field_type = types.Array(Mock())
        self.assertRaisesRegexp(ValidationError, "'1' is not an array-like sequence",
                                field_type.validate, 1)

    def test_given_field_type_when_validated_then_calls_field_type_validator_for_each_element(self):
        sub_type = Mock()
        field_type = types.Array(sub_type)

        element1, element2 = Mock(), Mock()

        field_type.validate([element1, element2])
        sub_type.validate.assert_any_call(element1)
        sub_type.validate.assert_any_call(element2)

    def test_given_extra_validators_when_validated_then_calls_extra_validators_for_each_element(self):
        validator1, validator2 = Mock(), Mock()
        element1, element2 = Mock(), Mock()

        field_type = types.Array(Mock(), validator1, validator2)
        field_type.validate([element1, element2])

        validator1.assert_any_call(element1)
        validator2.assert_any_call(element2)
