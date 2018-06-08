# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from hamcrest import assert_that, raises, calling, equal_to
from mock import Mock, sentinel

from xivo_dao.helpers.exception import InputError, NotFoundError, ResourceError

from xivo_confd.helpers.validator import (GetResource,
                                          MemberOfSequence,
                                          Optional,
                                          ResourceExists,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          ValidationAssociation,
                                          ValidationGroup,
                                          Validator)


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


class TestUniqueFieldChanged(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = UniqueFieldChanged('field', self.dao)

    def test_given_model_with_field_not_found_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.dao.find_by.return_value = None

        self.validator.validate(model)

    def test_given_model_with_same_id_was_found_then_validation_passes(self):
        model = Mock(field=sentinel.field, id=sentinel.id)

        self.dao.find_by.return_value = model

        self.validator.validate(model)

    def test_given_model_with_different_id_was_found_then_validation_fails(self):
        model = Mock(field=sentinel.field, id=sentinel.id)
        other_model = Mock(field=sentinel.field, id=sentinel.other_id)

        self.dao.find_by.return_value = other_model

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(ResourceError))


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

    def test_given_multiple_validators_for_field_then_all_validators_called(self):
        child_validator1 = Mock()
        child_validator2 = Mock()
        model = Mock(field='field')
        validator = Optional('field', child_validator1, child_validator2)

        validator.validate(model)

        child_validator1.validate.assert_called_once_with(model)
        child_validator2.validate.assert_called_once_with(model)


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


class TestValidationAssociation(unittest.TestCase):

    def test_when_validating_association_then_calls_common_and_association_validators(self):
        common = Mock(Validator)
        association = Mock(Validator)
        model = Mock()

        validator = ValidationAssociation(common=[common], association=[association])

        validator.validate_association(model)

        common.validate.assert_called_once_with(model)
        association.validate.assert_called_once_with(model)

    def test_when_validating_multiple_models_then_all_models_passed_to_validator(self):
        common = Mock(Validator)
        association = Mock(Validator)
        dissociation = Mock(Validator)
        model1 = Mock()
        model2 = Mock()

        validator = ValidationAssociation(common=[common], association=[association], dissociation=[dissociation])

        validator.validate_association(model1, model2)
        validator.validate_dissociation(model1, model2)

        common.validate.assert_called_with(model1, model2)
        association.validate.assert_called_once_with(model1, model2)
        dissociation.validate.assert_called_once_with(model1, model2)

    def test_when_validating_dissociation_then_calls_common_and_dissociation_validators(self):
        common = Mock(Validator)
        dissociation = Mock(Validator)
        model = Mock()

        validator = ValidationAssociation(common=[common], dissociation=[dissociation])

        validator.validate_dissociation(model)

        common.validate.assert_called_once_with(model)
        dissociation.validate.assert_called_once_with(model)
