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

from mock import patch, Mock
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.user_line.model import UserLine
from xivo_dao.resources.user_voicemail.model import UserVoicemail

from xivo_confd.resources.user_voicemail import validator


class TestValidator(unittest.TestCase):

    def test_validate_association_missing_parameters(self):
        user_voicemail = UserVoicemail()

        self.assertRaises(InputError, validator.validate_association, user_voicemail)

    def test_validate_association_wrong_parameter_type_for_enabled(self):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2, enabled=1)

        self.assertRaises(InputError, validator.validate_association, user_voicemail)

    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_association_when_user_does_not_exist(self, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        user_get.side_effect = NotFoundError
        self.assertRaises(InputError, validator.validate_association, user_voicemail)
        user_get.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.voicemail.dao.get')
    def test_validate_association_when_voicemail_does_not_exist(self, voicemail_get, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        voicemail_get.side_effect = NotFoundError
        self.assertRaises(InputError, validator.validate_association, user_voicemail)
        voicemail_get.assert_called_once_with(user_voicemail.voicemail_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.voicemail.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_validate_association_voicemail_when_user_has_no_line(self, find_all_by_user_id, voicemail_get, user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        find_all_by_user_id.return_value = []

        self.assertRaises(ResourceError, validator.validate_association, user_voicemail)
        find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.voicemail.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.user_voicemail.dao.get_by_user_id')
    def test_validate_association_voicemail_when_user_already_has_a_voicemail(self,
                                                                              voicemail_get_by_user_id,
                                                                              find_all_by_user_id,
                                                                              voicemail_get,
                                                                              user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        find_all_by_user_id.return_value = [Mock(UserLine)]
        voicemail_get_by_user_id.side_effect = Mock(UserVoicemail)

        self.assertRaises(ResourceError, validator.validate_association, user_voicemail)
        voicemail_get_by_user_id.assert_called_once_with(user_voicemail.user_id)
        find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.voicemail.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.user_voicemail.dao.get_by_user_id')
    def test_validate_association(self,
                                  voicemail_get_by_user_id,
                                  find_all_by_user_id,
                                  voicemail_get,
                                  user_get):
        user_voicemail = UserVoicemail(user_id=1, voicemail_id=2)

        find_all_by_user_id.return_value = [Mock(UserLine)]
        voicemail_get_by_user_id.side_effect = NotFoundError

        validator.validate_association(user_voicemail)
        user_get.assert_called_once_with(user_voicemail.user_id)
        voicemail_get.assert_called_once_with(user_voicemail.voicemail_id)
        find_all_by_user_id.assert_called_once_with(user_voicemail.user_id)
        voicemail_get_by_user_id.assert_called_once_with(user_voicemail.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation_user_not_exists(self, patch_dao):
        user_voicemail = Mock(UserVoicemail, user_id=3)

        patch_dao.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_dissociation, user_voicemail)

    @patch('xivo_dao.resources.voicemail.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation_no_voicemail(self, user_dao_get, voicemail_dao_get):
        user_voicemail = Mock(UserVoicemail, user_id=3, voicemail_id=4)

        user_dao_get.return_value = Mock()
        voicemail_dao_get.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_dissociation, user_voicemail)

    @patch('xivo_dao.resources.voicemail.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation(self, user_dao_get, voicemail_dao_get):
        user_voicemail = Mock(UserVoicemail, user_id=3, voicemail_id=4)

        validator.validate_dissociation(user_voicemail)
        user_dao_get.assert_called_once_with(user_voicemail.user_id)
        voicemail_dao_get.assert_called_once_with(user_voicemail.voicemail_id)
