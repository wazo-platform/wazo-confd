# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
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

from mock import Mock, sentinel

from xivo_confd.plugins.user.validator import (NoEmptyFieldWhenEnabled,
                                               NoLineAssociated,
                                               NoVoicemailAssociated)
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.resources.user_voicemail.model import UserVoicemail


class TestValidateNoVoicemailAssociated(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = NoVoicemailAssociated(self.dao)

    def test_given_voicemail_associated_then_validation_fails(self):
        user = Mock(User, id=sentinel.id)
        self.dao.find_by_user_id.return_value = Mock(UserVoicemail,
                                                     user_id=sentinel.user_id,
                                                     voicemail_id=sentinel.voicemail_id)

        self.assertRaises(ResourceError, self.validator.validate, user)

        self.dao.find_by_user_id.assert_called_once_with(user.id)

    def test_given_no_voicemail_associated_then_validation_passes(self):
        user = Mock(User, id=sentinel.id)
        self.dao.find_by_user_id.return_value = None

        self.validator.validate(user)

        self.dao.find_by_user_id.assert_called_once_with(user.id)


class TestValidateNoLineAssociated(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = NoLineAssociated(self.dao)

    def test_given_line_associated_then_validation_fails(self):
        user = Mock(User, id=sentinel.id)
        self.dao.find_all_by_user_id.return_value = [Mock(UserLine, line_id=sentinel.line_id)]

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

    def test_given_required_field_are_none_and_enabled_true_when_validating_then_raises_error(self):
        self.model.destination_field = None
        self.model.enabled_field = True

        self.assertRaises(ResourceError, self.validator.validate, self.model)

    def test_given_required_field_are_not_none_and_enabled_true_when_validation_passed(self):
        self.model.destination_field = '123'
        self.model.enabled_field = True

        self.validator.validate(self.model)

    def test_given_required_field_are_none_and_enabled_false_when_validation_passed(self):
        self.model.destination_field = None
        self.model.enabled_field = False

        self.validator.validate(self.model)

    def test_given_required_field_are_not_none_and_enabled_false_when_validation_passed(self):
        self.model.destination_field = '123'
        self.model.enabled_field = False

        self.validator.validate(self.model)
