# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel

from hamcrest import assert_that, calling, raises

from xivo_dao.alchemy.callfiltermember import Callfiltermember as CallFilterMember
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import InputError, ResourceError
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate
from xivo_dao.resources.func_key.model import (
    BSFilterDestination,
    CustomDestination,
    ForwardDestination,
    FuncKey,
    ParkPositionDestination,
    ServiceDestination,
)

from xivo_confd.helpers.validator import Validator
from xivo_confd.plugins.func_key.validator import FuncKeyMappingValidator
from xivo_confd.plugins.func_key.validator import (
    BSFilterValidator,
    CustomValidator,
    ForwardValidator,
    FuncKeyModelValidator,
    ParkPositionValidator,
    PrivateTemplateValidator,
    SimilarFuncKeyValidator,
)


class TestSimilarFuncKeyValidator(unittest.TestCase):

    def setUp(self):
        self.validator = SimilarFuncKeyValidator()

    def test_when_template_empty_then_validation_passes(self):
        template = FuncKeyTemplate()

        self.validator.validate(template)

    def test_when_template_has_a_single_func_key_then_validation_passes(self):
        funckey = FuncKey(destination=CustomDestination(exten='1234'))
        template = FuncKeyTemplate(keys={1: funckey})

        self.validator.validate(template)

    def test_when_template_has_two_func_keys_with_different_destination_then_validation_passes(self):
        template = FuncKeyTemplate(keys={1: FuncKey(destination=CustomDestination(exten='1234')),
                                         2: FuncKey(destination=ServiceDestination(service='enablednd'))})

        self.validator.validate(template)

    def test_when_template_has_two_func_keys_with_same_destination_then_raises_error(self):
        destination = CustomDestination(exten='1234')
        template = FuncKeyTemplate(keys={1: FuncKey(destination=destination),
                                         2: FuncKey(destination=destination)})

        assert_that(calling(self.validator.validate).with_args(template),
                    raises(ResourceError))


class TestPrivateTemplateValidator(unittest.TestCase):

    def setUp(self):
        self.validator = PrivateTemplateValidator()

    def test_when_validating_private_template_then_raises_error(self):
        template = FuncKeyTemplate(private=True)

        assert_that(calling(self.validator.validate).with_args(template),
                    raises(ResourceError))

    def test_when_validating_public_template_then_validation_passes(self):
        template = FuncKeyTemplate(private=False)

        self.validator.validate(template)


class TestFuncKeyMappingValidator(unittest.TestCase):

    def setUp(self):
        self.funckey_validator = Mock(FuncKeyModelValidator)
        self.validator = FuncKeyMappingValidator(self.funckey_validator)

    def test_given_func_key_mapping_when_validating_then_validates_each_func_key(self):
        first_funckey = Mock(FuncKey)
        second_funckey = Mock(FuncKey)

        template = FuncKeyTemplate(keys={1: first_funckey,
                                         2: second_funckey})

        self.validator.validate(template)

        self.funckey_validator.validate.assert_any_call(first_funckey)
        self.funckey_validator.validate.assert_any_call(second_funckey)


class TestFuncKeyValidator(unittest.TestCase):

    def setUp(self):
        self.first_dest_validator = Mock(Validator)
        self.second_dest_validator = Mock(Validator)
        self.validator = FuncKeyModelValidator({'foobar': [self.first_dest_validator,
                                                           self.second_dest_validator]})

    def test_given_no_validator_for_destination_when_validating_then_raises_error(self):
        destination = Mock(type='spam')

        model = FuncKey(destination=destination)

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_multiple_validators_for_destination_when_validating_then_calls_each_validator(self):
        destination = Mock(type='foobar')
        model = FuncKey(destination=destination)

        self.validator.validate(model)

        self.first_dest_validator.validate.assert_called_once_with(destination)
        self.second_dest_validator.validate.assert_called_once_with(destination)

    def test_given_label_with_invalid_characters_when_validating_then_raises_error(self):
        model = FuncKey(label='hello\n',
                        destination=Mock(type='foobar'))

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

        model = FuncKey(label='\rhello',
                        destination=Mock(type='foobar'))

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

        model = FuncKey(label='hel;lo',
                        destination=Mock(type='foobar'))

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))


class TestForwardValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ForwardValidator()

    def test_given_exten_contains_invalid_characters_then_validation_raises_error(self):
        destination = ForwardDestination(forward='noanswer', exten='hello\n')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_exten_contains_valid_characters_then_validation_passes(self):
        destination = ForwardDestination(forward='noanswer', exten='hello')

        self.validator.validate(destination)


class TestParkPositionValidator(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.dao.find_park_position_range.return_value = (701, 750)
        self.validator = ParkPositionValidator(self.dao)

    def test_given_position_under_minimum_then_raises_error(self):
        destination = ParkPositionDestination(position=600)

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_position_over_maximum_then_raises_error(self):
        destination = ParkPositionDestination(position=800)

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_position_on_minimum_position_then_validation_passes(self):
        destination = ParkPositionDestination(position=701)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()

    def test_given_position_on_maximum_position_then_validation_passes(self):
        destination = ParkPositionDestination(position=750)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()

    def test_given_position_inside_range_then_validation_passes(self):
        destination = ParkPositionDestination(position=710)

        self.validator.validate(destination)

        self.dao.find_park_position_range.assert_called_once_with()


class TestCustomValidator(unittest.TestCase):

    def setUp(self):
        self.validator = CustomValidator()

    def test_given_exten_contains_invalid_characters_then_validation_raises_error(self):
        destination = CustomDestination(exten='1234\n')

        assert_that(calling(self.validator.validate).with_args(destination),
                    raises(InputError))

    def test_given_exten_contains_valid_characters_then_validation_passes(self):
        destination = CustomDestination(exten='1234')

        self.validator.validate(destination)


class TestBSFilterValidator(unittest.TestCase):

    def setUp(self):
        self.user = User(id=sentinel.user_id)
        self.funckey = FuncKey(destination=BSFilterDestination(filter_member_id=sentinel.filter_member_id))

        self.validator = BSFilterValidator()

    def test_when_func_key_does_not_have_bsfilter_destination_then_validation_passes(self):
        funckey = FuncKey(destination=CustomDestination(exten='1234'))

        self.validator.validate(self.user, funckey)

    def test_when_user_is_not_member_of_a_filter_then_raises_error(self):
        user = self.user
        user.call_filter_recipients = []
        user.call_filter_surrogates = []

        assert_that(calling(self.validator.validate).with_args(self.user, self.funckey),
                    raises(ResourceError))

    def test_when_user_is_recipient_of_a_filter_then_validation_passes(self):
        user = self.user
        user.call_filter_recipients = [CallFilterMember()]

        self.validator.validate(self.user, self.funckey)

    def test_when_user_is_surrogate_of_a_filter_then_validation_passes(self):
        user = self.user
        user.call_filter_surrogates = [CallFilterMember()]

        self.validator.validate(self.user, self.funckey)
