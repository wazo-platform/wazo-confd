# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, sentinel

from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.exception import ResourceError

from ..validator import NoEmptyFieldWhenEnabled, NoLineAssociated, NoVoicemailAssociated


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


class TestValidateNoLineAssociated(unittest.TestCase):
    def setUp(self):
        self.dao = Mock()
        self.validator = NoLineAssociated(self.dao)

    def test_given_line_associated_then_validation_fails(self):
        user = Mock(User, id=sentinel.id)
        self.dao.find_all_by_user_id.return_value = [
            Mock(UserLine, line_id=sentinel.line_id)
        ]

        self.assertRaises(ResourceError, self.validator.validate, user)

        self.dao.find_all_by_user_id.assert_called_once_with(user.id)

    def test_given_no_line_associated_then_validation_passes(self):
        user = Mock(User, id=sentinel.id)
        self.dao.find_all_by_user_id.return_value = []

        self.validator.validate(user)

        self.dao.find_all_by_user_id.assert_called_once_with(user.id)


class TestNoEmptyFieldWhenEnabled(unittest.TestCase):
    def setUp(self):
        self.validator = NoEmptyFieldWhenEnabled('destination_field', 'enabled_field')
        self.model = Mock()

    def test_given_required_field_are_none_and_enabled_true_when_validating_then_raises_error(
        self
    ):
        self.model.destination_field = None
        self.model.enabled_field = True

        self.assertRaises(ResourceError, self.validator.validate, self.model)

    def test_given_required_field_are_not_none_and_enabled_true_when_validation_passed(
        self
    ):
        self.model.destination_field = '123'
        self.model.enabled_field = True

        self.validator.validate(self.model)

    def test_given_required_field_are_none_and_enabled_false_when_validation_passed(
        self
    ):
        self.model.destination_field = None
        self.model.enabled_field = False

        self.validator.validate(self.model)

    def test_given_required_field_are_not_none_and_enabled_false_when_validation_passed(
        self
    ):
        self.model.destination_field = '123'
        self.model.enabled_field = False

        self.validator.validate(self.model)
