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

from xivo_restapi.helpers.premacop.field import Field
from xivo_restapi.helpers.premacop.types import FieldType
from xivo_restapi.helpers.premacop.errors import ValidationError


class TestField(unittest.TestCase):

    def test_given_no_validators_when_field_validated_then_calls_field_type_validator(self):
        field_type = Mock(FieldType)
        field = Field('name', field_type)
        value = Mock()

        field.validate(value)

        field_type.validate.assert_called_once_with(value)

    def test_given_one_validator_when_field_validated_then_calls_validator(self):
        field_type = Mock(FieldType)
        validator = Mock()

        field = Field('name', field_type, validator)
        value = Mock()

        field.validate(value)

        validator.assert_called_once_with(value)

    def test_given_validator_on_action_when_field_validated_then_calls_action_validator(self):
        field_type = Mock(FieldType)
        action_validator = Mock()
        value = Mock()

        field = Field('name', field_type, create=action_validator)

        field.validate(value, 'create')

        action_validator.assert_called_once_with(value)

    def test_given_multiple_validators_then_field_validated_then_calls_all_validators(self):
        field_type = Mock(FieldType)
        validator1 = Mock()
        validator2 = Mock()
        action_validator1 = Mock()
        action_validator2 = Mock()
        value = Mock()

        field = Field('name', field_type, validator1, validator2, create=[action_validator1, action_validator2])

        field.validate(value, 'create')

        field_type.validate.assert_called_once_with(value)
        validator1.assert_called_once_with(value)
        validator2.assert_called_once_with(value)
        action_validator1.assert_called_once_with(value)
        action_validator2.assert_called_once_with(value)

    def test_given_validation_error_raised_then_reformats_error(self):
        field_type = Mock(FieldType)
        field_type.validate.side_effect = ValidationError('message')
        value = Mock()

        field = Field('name', field_type)

        self.assertRaisesRegexp(ValidationError, "Error while validating field 'name': message",
                                field.validate, value)
