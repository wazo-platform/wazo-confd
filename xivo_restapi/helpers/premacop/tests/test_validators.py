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
from xivo_restapi.helpers.premacop import validators
from xivo_restapi.helpers.premacop.errors import ValidationError


class TestRequiredValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.Required()

    def test_given_value_is_none_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "field is required",
                                self.validator, None)

    def test_given_value_is_not_none_then_validation_passes(self):
        self.validator(1)


class TestLengthValidator(unittest.TestCase):

    def test_given_value_is_none_then_validation_passes(self):
        validator = validators.Length(minimum=1)
        validator(None)

    def test_given_value_is_shorter_than_minimum_then_raises_error(self):
        validator = validators.Length(minimum=1)
        self.assertRaisesRegexp(ValidationError, "minimum length is 1",
                                validator, "")

    def test_given_value_is_equal_to_minimum_then_validation_passes(self):
        validator = validators.Length(minimum=1)
        validator("a")

    def test_given_value_is_longer_than_maximum_then_raises_error(self):
        validator = validators.Length(maximum=1)
        self.assertRaisesRegexp(ValidationError, "maximum length is 1",
                                validator, "ab")

    def test_given_value_is_equal_to_maximum_then_validation_passes(self):
        validator = validators.Length(maximum=1)
        validator("a")


class TestPositiveValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.Positive()

    def test_given_value_is_none_then_validation_passes(self):
        self.validator(None)

    def test_given_value_is_below_zero_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "must be a positive number",
                                self.validator, -1)

    def test_given_value_is_zero_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "must be a positive number",
                                self.validator, 0)

    def test_given_value_is_over_zero_then_validation_passes(self):
        self.validator(1)


class TestChoiceValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.Choice(['a', 'b'])

    def test_given_value_is_none_then_validation_passes(self):
        self.validator(None)

    def test_given_value_is_not_in_choices_then_raises_error(self):
        self.assertRaisesRegexp(ValidationError, "must be one of the following choices: a, b",
                                self.validator, 'c')

    def test_given_value_is_in_choices_then_passes(self):
        self.validator('b')
