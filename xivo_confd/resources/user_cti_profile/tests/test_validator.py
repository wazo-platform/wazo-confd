# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from mock import patch
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import InputError

from xivo_dao.resources.user_cti_profile import validator
from xivo_dao.resources.user_cti_profile.model import UserCtiProfile
from xivo_dao.resources.user.model import User


class TestUserCtiProfileValidator(unittest.TestCase):

    @patch('xivo_dao.resources.cti_profile.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_edition(self, patch_get_user, patch_get_profile):
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2, enabled=True)
        validator.validate_edit(user_cti_profile)

    @patch('xivo_dao.resources.cti_profile.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_edition_unexisting_user(self, patch_get_user, patch_get_profile):
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2, enabled=True)
        patch_get_user.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_edit, user_cti_profile)
        patch_get_user.assert_called_with(user_cti_profile.user_id)

    @patch('xivo_dao.resources.cti_profile.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_edition_unexisting_profile(self, patch_get_user, patch_get_cti_profile):
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2, enabled=True)
        patch_get_cti_profile.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_edit, user_cti_profile)
        patch_get_cti_profile.assert_called_with(user_cti_profile.cti_profile_id)

    @patch('xivo_dao.resources.cti_profile.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_edition_null_profile(self, patch_get_user, patch_get_cti_profile):
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=None, enabled=True)
        validator.validate_edit(user_cti_profile)

        self.assertFalse(patch_get_cti_profile.called, "CTI profile dao should not have been called")

    @patch('xivo_dao.resources.cti_profile.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_edition_missing_username_password(self, patch_get_user, patch_get_cti_profile):
        user_cti_profile = UserCtiProfile(user_id=1, cti_profile_id=2, enabled=True)
        patch_get_user.return_value = User(id=1, username=None, password=None)

        self.assertRaises(ResourceError, validator.validate_edit, user_cti_profile)
