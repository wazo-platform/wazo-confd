# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from mock import patch, Mock, sentinel

from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.user.model import User
from xivo_dao.resources.user_line.model import UserLine
from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.resources.users import validator


class TestUserValidator(unittest.TestCase):

    @patch('xivo_confd.resources.users.validator.validate_caller_id')
    @patch('xivo_confd.resources.users.validator.validate_model')
    @patch('xivo_confd.resources.users.validator.validate_private_template_id_is_not_set')
    def test_validate_create(self, validate_template, validate_model, validate_caller_id):
        user = Mock(User)

        validator.validate_create(user)
        validate_model.assert_called_once_with(user)
        validate_template.assert_called_once_with(user)
        validate_caller_id.assert_called_once_with(user, required=False)

    @patch('xivo_confd.resources.users.validator.validate_caller_id')
    @patch('xivo_confd.resources.users.validator.validate_model')
    @patch('xivo_confd.resources.users.validator.validate_private_template_id_does_not_change')
    def test_validate_edit(self, validate_template, validate_model, validate_caller_id):
        user = Mock(User)

        validator.validate_edit(user)
        validate_model.assert_called_once_with(user)
        validate_template.assert_called_once_with(user)
        validate_caller_id.assert_called_once_with(user, required=True)

    @patch('xivo_confd.resources.users.validator.validate_user_not_associated')
    @patch('xivo_confd.resources.users.validator.validate_user_exists')
    def test_validate_delete(self, validate_user_exists, validate_user_not_associated):
        user = Mock(User)

        validator.validate_delete(user)
        validate_user_exists.assert_called_once_with(user)
        validate_user_not_associated.assert_called_once_with(user)


class TestValidateModel(unittest.TestCase):

    def test_validate_model_no_properties(self):
        user = User()

        self.assertRaises(InputError, validator.validate_model, user)

    def test_validate_model_empty_firstname(self):
        firstname = ''

        user = User(firstname=firstname)

        self.assertRaises(InputError, validator.validate_model, user)

    def test_validate_model_invalid_password(self):
        password = 'ewr'

        user = User(firstname='toto',
                    password=password)

        self.assertRaises(InputError, validator.validate_model, user)

    def test_validate_model_valid_password(self):
        password = 'ewree'

        user = User(firstname='toto',
                    password=password)

        validator.validate_model(user)

    def test_validate_model_invalid_mobilephonenumber_alpha(self):
        user = User(firstname='toto',
                    mobile_phone_number='mobilephonenumber')

        self.assertRaises(InputError, validator.validate_model, user)

    def test_validate_model_invalid_mobilephonenumber_alphanum(self):
        user = User(firstname='toto',
                    mobile_phone_number='abcd1234')

        self.assertRaises(InputError, validator.validate_model, user)

    def test_validate_model_basic_mobilephonenumber(self):
        user = User(firstname='toto',
                    mobile_phone_number='1234')

        validator.validate_model(user)

    def test_validate_model_international_mobilephonenumber(self):
        user = User(firstname='toto',
                    mobile_phone_number='+011224657453*77#23')

        validator.validate_model(user)


class TestValdateCallerId(unittest.TestCase):

    def test_given_invalid_caller_id_when_validating_then_raises_error(self):
        user = User(caller_id='toto')

        self.assertRaises(InputError, validator.validate_caller_id, user)

    def test_given_valid_caller_id_when_validating_then_validation_passes(self):
        user = User(caller_id='"toto" <1000>')

        validator.validate_caller_id(user)

    def test_given_no_caller_id_when_caller_id_is_required_then_raises_error(self):
        user = User()

        self.assertRaises(InputError, validator.validate_caller_id, user, required=True)

    def test_given_no_caller_id_when_caller_id_is_not_required_then_validation_passes(self):
        user = User()

        validator.validate_caller_id(user, required=False)

    def test_given_caller_id_is_invalid_and_not_required_when_validating_then_raises_error(self):
        user = User(caller_id='toto')

        self.assertRaises(InputError, validator.validate_caller_id, user, required=False)


class TestValidateUserNotAssociated(unittest.TestCase):

    @patch('xivo_confd.resources.users.validator.validate_not_associated_to_line')
    @patch('xivo_confd.resources.users.validator.validate_not_associated_to_voicemail')
    def test_validate_user_not_associated(self, validate_not_associated_to_voicemail,
                                          validate_not_associated_to_line):

        user = Mock(User)

        validator.validate_user_not_associated(user)

        validate_not_associated_to_line.assert_called_once_with(user)
        validate_not_associated_to_voicemail.assert_called_once_with(user)


class TestValidateNotAssociatedToLine(unittest.TestCase):

    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_when_not_associated_to_line(self, find_all_by_user_id):
        find_all_by_user_id.return_value = []

        user = Mock(User, id=1)

        validator.validate_not_associated_to_line(user)

        find_all_by_user_id.assert_called_once_with(user.id)

    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_when_associated_to_line(self, find_all_by_user_id):
        find_all_by_user_id.return_value = [Mock(UserLine, user_id=1, line_id=2)]

        user = Mock(User, id=1)

        self.assertRaises(ResourceError, validator.validate_not_associated_to_line, user)

        find_all_by_user_id.assert_called_once_with(user.id)


class TestValidateUserExists(unittest.TestCase):

    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_user_exists(self, dao_get):
        dao_get.return_value = Mock(User)

        user = Mock(User, id=1)

        validator.validate_user_exists(user)

        dao_get.assert_called_once_with(user.id)


class TestValidateNotAssociatedToVoicemail(unittest.TestCase):

    @patch('xivo_dao.resources.user_voicemail.dao.find_by_user_id')
    def test_when_not_associated_to_voicemail(self, find_all_by_user_id):
        find_all_by_user_id.return_value = []

        user = Mock(User, id=1)

        validator.validate_not_associated_to_voicemail(user)

        find_all_by_user_id.assert_called_once_with(user.id)

    @patch('xivo_dao.resources.user_voicemail.dao.find_by_user_id')
    def test_when_associated_to_voicemail(self, find_by_user_id):
        find_by_user_id.return_value = Mock(UserVoicemail, user_id=1, voicemail_id=2)

        user = Mock(User, id=1)

        self.assertRaises(ResourceError, validator.validate_not_associated_to_voicemail, user)

        find_by_user_id.assert_called_once_with(user.id)


class TestValidatePrivateTemplateIDIsNotSet(unittest.TestCase):

    def test_when_template_id_is_not_set(self):
        user = Mock(User, private_template_id=None)

        validator.validate_private_template_id_is_not_set(user)

    def test_when_template_id_is_set(self):
        user = Mock(User, private_template_id=12)

        self.assertRaises(InputError, validator.validate_private_template_id_is_not_set, user)


@patch('xivo_dao.resources.user.dao.get', return_value=Mock(User, private_template_id=sentinel.template_id))
class TestValidatePrivateTemplateIDDoesNotChange(unittest.TestCase):

    def test_when_template_id_does_not_change(self, get_user):
        user = Mock(User, id=1, private_template_id=sentinel.template_id)

        validator.validate_private_template_id_does_not_change(user)

    def test_when_template_id_does_change(self, get_user):
        user = Mock(User, id=1, private_template_id=sentinel.template_id2)

        self.assertRaises(InputError, validator.validate_private_template_id_does_not_change, user)
