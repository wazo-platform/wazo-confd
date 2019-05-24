# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import patch, Mock
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers.exception import InputError

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from xivo_confd.plugins.user_cti_profile import validator


class TestUserCtiProfileValidator(unittest.TestCase):

    @patch('xivo_dao.resources.cti_profile.dao.get', Mock())
    def test_validate_edition(self):
        user = Mock(User)
        cti_profile_id = 2
        validator.validate_edit(user, cti_profile_id)

    @patch('xivo_dao.resources.cti_profile.dao.get')
    def test_validate_edition_unexisting_profile(self, patch_get_cti_profile):
        user = Mock()
        cti_profile_id = 2
        patch_get_cti_profile.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_edit, user, cti_profile_id)
        patch_get_cti_profile.assert_called_with(cti_profile_id)

    @patch('xivo_dao.resources.cti_profile.dao.get')
    def test_validate_edition_null_profile(self, patch_get_cti_profile):
        user = Mock()
        cti_profile_id = None
        validator.validate_edit(user, cti_profile_id)

        self.assertFalse(patch_get_cti_profile.called, "CTI profile dao should not have been called")

    @patch('xivo_dao.resources.cti_profile.dao.get')
    def test_validate_edition_missing_username_password(self, patch_get_cti_profile):
        user = Mock(User, id=1, cti_enabled=True, username=None, password=None)
        cti_profile_id = 2

        self.assertRaises(ResourceError, validator.validate_edit, user, cti_profile_id)
