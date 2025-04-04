# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock, sentinel

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import ResourceError

from ..validator import NoEmptyFieldWhenEnabled, NoVoicemailAssociated


class TestValidateNoVoicemailAssociated(unittest.TestCase):
    def setUp(self):
        self.dao = Mock()
        self.validator = NoVoicemailAssociated()

    def test_given_voicemail_associated_then_validation_fails(self):
        user = Mock(User, id=sentinel.id, voicemail=Mock(id=sentinel.id))

        self.assertRaises(ResourceError, self.validator.validate, user)

    def test_given_no_voicemail_associated_then_validation_passes(self):
        user = Mock(User, id=sentinel.id, voicemail=None)

        self.validator.validate(user)


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
