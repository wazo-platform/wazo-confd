# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock

from xivo_dao.helpers.exception import ResourceError

from ..validator import NoEmptyFieldWhenEnabled


class TestNoEmptyFieldWhenEnabled(unittest.TestCase):
    def setUp(self):
        self.validator = NoEmptyFieldWhenEnabled('destination_field', 'enabled_field')
        self.model = Mock()

    def test_given_required_field_are_none_and_enabled_true_when_validating_then_raises_error(
        self,
    ):
        self.model.destination_field = None
        self.model.enabled_field = True

        self.assertRaises(ResourceError, self.validator.validate, self.model)

    def test_given_required_field_are_not_none_and_enabled_true_when_validation_passed(
        self,
    ):
        self.model.destination_field = '123'
        self.model.enabled_field = True

        self.validator.validate(self.model)

    def test_given_required_field_are_none_and_enabled_false_when_validation_passed(
        self,
    ):
        self.model.destination_field = None
        self.model.enabled_field = False

        self.validator.validate(self.model)

    def test_given_required_field_are_not_none_and_enabled_false_when_validation_passed(
        self,
    ):
        self.model.destination_field = '123'
        self.model.enabled_field = False

        self.validator.validate(self.model)
