# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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
from hamcrest import assert_that, raises, calling, equal_to
from mock import Mock, sentinel

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.helpers.exception import InputError, NotFoundError, ResourceError

from xivo_confd.helpers.validator import RequiredFields, GetResource, \
    ResourceExists, FindResource, Validator, Optional, MemberOfSequence, \
    ValidationGroup, AssociationValidator, MissingFields, UniqueField, RegexField


class TestRequiredFields(unittest.TestCase):

    def setUp(self):
        self.validator = RequiredFields('field1', 'field2')
        self.model = Mock()

    def test_given_required_fields_are_none_when_validating_then_raises_error(self):
        self.model.field1 = None
        self.model.field2 = None

        self.assertRaises(InputError, self.validator.validate, self.model)

    def test_given_required_fields_have_a_value_when_validating_then_validation_passes(self):
        self.model.field1 = 'value1'
        self.model.field2 = 'value2'

        self.validator.validate(self.model)


class TestMissingFields(unittest.TestCase):

    def setUp(self):
        self.validator = MissingFields()

    def test_given_missing_fields_when_validating_then_raises_error(self):
        model = Mock(NewModel)
        model.missing_parameters.return_value = ['foobar']

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_no_missing_fields_when_validating_then_passes(self):
        model = Mock(NewModel)
        model.missing_parameters.return_value = []

        self.validator.validate(model)


class TestGetResource(unittest.TestCase):

    def setUp(self):
        self.dao_get = Mock()
        self.validator = GetResource('field', self.dao_get)

    def test_given_resource_does_not_exist_then_raises_error(self):
        model = Mock(field=sentinel.field)

        self.dao_get.side_effect = NotFoundError

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_resource_exists_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.validator.validate(model)

        self.dao_get.assert_called_once_with(model.field)


class TestFindResource(unittest.TestCase):

    def setUp(self):
        self.dao_find = Mock()
        self.validator = FindResource('field', self.dao_find)

    def test_given_resource_does_not_exist_then_raises_error(self):
        model = Mock(field=sentinel.field)

        self.dao_find.return_value = None

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_resource_exists_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.validator.validate(model)

        self.dao_find.assert_called_once_with(model.field)


class TestUniqueField(unittest.TestCase):

    def setUp(self):
        self.dao_find = Mock()
        self.validator = UniqueField('field', self.dao_find)

    def test_given_model_with_field_not_found_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.dao_find.return_value = None

        self.validator.validate(model)

    def test_given_model_with_field_was_found_then_validation_fails(self):
        model = Mock(field=sentinel.field)

        self.dao_find.return_value = model

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(ResourceError))


class TestRegexField(unittest.TestCase):

    def setUp(self):
        self.regex = Mock()
        self.model = Mock(field=sentinel.field)
        self.validator = RegexField('field', self.regex)

    def test_given_regex_matches_then_validation_passes(self):
        self.validator.validate(self.model)

        self.regex.match.assert_called_once_with(sentinel.field)

    def test_given_regex_does_not_match_then_validation_fails(self):
        self.regex.match.return_value = None

        assert_that(calling(self.validator.validate).with_args(self.model),
                    raises(InputError))


class TestResourceExists(unittest.TestCase):

    def setUp(self):
        self.dao_exist = Mock()
        self.validator = ResourceExists('field', self.dao_exist)

    def test_given_resource_does_not_exist_then_raises_error(self):
        model = Mock(field=sentinel.field)

        self.dao_exist.return_value = False

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_resource_exists_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.dao_exist.return_value = True

        self.validator.validate(model)

        self.dao_exist.assert_called_once_with(model.field)


class TestOptional(unittest.TestCase):

    def setUp(self):
        self.child_validator = Mock(Validator)
        self.validator = Optional('field', self.child_validator)

    def test_given_field_is_none_then_validation_passes(self):
        model = Mock(field=None)

        self.validator.validate(model)

        assert_that(self.child_validator.validate.called, equal_to(False))

    def test_given_field_has_value_then_child_validator_called(self):
        model = Mock(field=sentinel.field)

        self.validator.validate(model)

        self.child_validator.validate.assert_called_once_with(model)


class TestMemberOfSequence(unittest.TestCase):

    def setUp(self):
        self.dao_list = Mock()
        self.validator = MemberOfSequence('field', self.dao_list)

    def test_given_field_not_in_list_of_items_then_raises_error(self):
        model = Mock(field='value')
        self.dao_list.return_value = []

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_field_in_list_then_validation_passes(self):
        model = Mock(field='value')
        self.dao_list.return_value = ['value']

        self.validator.validate(model)


class TestValidationGroup(unittest.TestCase):

    def test_when_validating_create_then_calls_common_and_create_validators(self):
        common = Mock(Validator)
        create = Mock(Validator)
        model = Mock()

        validator = ValidationGroup(common=[common], create=[create])

        validator.validate_create(model)

        common.validate.assert_called_once_with(model)
        create.validate.assert_called_once_with(model)

    def test_when_validating_edit_then_calls_common_and_edit_validators(self):
        common = Mock(Validator)
        edit = Mock(Validator)
        model = Mock()

        validator = ValidationGroup(common=[common], edit=[edit])

        validator.validate_edit(model)

        common.validate.assert_called_once_with(model)
        edit.validate.assert_called_once_with(model)

    def test_when_validating_delete_then_calls_common_and_delete_validators(self):
        common = Mock(Validator)
        delete = Mock(Validator)
        model = Mock()

        validator = ValidationGroup(common=[common], delete=[delete])

        validator.validate_delete(model)

        common.validate.assert_called_once_with(model)
        delete.validate.assert_called_once_with(model)


class TestAssociationValidator(unittest.TestCase):

    def test_when_validating_association_then_calls_common_and_association_validators(self):
        common = Mock(Validator)
        association = Mock(Validator)
        model = Mock()

        validator = AssociationValidator(common=[common], association=[association])

        validator.validate_association(model)

        common.validate.assert_called_once_with(model)
        association.validate.assert_called_once_with(model)

    def test_when_validating_multiple_models_then_all_models_passed_to_validator(self):
        common = Mock(Validator)
        association = Mock(Validator)
        dissociation = Mock(Validator)
        model1 = Mock()
        model2 = Mock()

        validator = AssociationValidator(common=[common], association=[association], dissociation=[dissociation])

        validator.validate_association(model1, model2)
        validator.validate_dissociation(model1, model2)

        common.validate.assert_called_with(model1, model2)
        association.validate.assert_called_once_with(model1, model2)
        dissociation.validate.assert_called_once_with(model1, model2)

    def test_when_validating_dissociation_then_calls_common_and_dissociation_validators(self):
        common = Mock(Validator)
        dissociation = Mock(Validator)
        model = Mock()

        validator = AssociationValidator(common=[common], dissociation=[dissociation])

        validator.validate_dissociation(model)

        common.validate.assert_called_once_with(model)
        dissociation.validate.assert_called_once_with(model)
