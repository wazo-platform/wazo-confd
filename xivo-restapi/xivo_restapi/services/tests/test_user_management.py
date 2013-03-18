# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock, call
from xivo_dao import user_dao
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.service_data_model.user_sdm import UserSdm
from xivo_restapi.services.user_management import UserManagement
from xivo_restapi.services.utils.exceptions import NoSuchElementException
import unittest
from xivo_dao.mapping_alchemy_sdm.user_mapping import UserMapping
import copy
from xivo_restapi.services.voicemail_management import VoicemailManagement


class TestUserManagement(unittest.TestCase):

    def setUp(self):
        self._userManager = UserManagement()
        self.user_mapping = Mock(UserMapping)
        self._userManager.user_mapping = self.user_mapping
        self.voicemail_manager = Mock(VoicemailManagement)
        self._userManager.voicemail_manager = self.voicemail_manager

    def test_get_all_users(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user1.cti_profile_id = 1
        user2 = UserFeatures()
        user2.firstname = 'test2'
        user_sdm1 = UserSdm()
        user_sdm2 = UserSdm()
        sdm_users = [user_sdm1, user_sdm2]
        user_dao.get_all = Mock()
        user_dao.get_all.return_value = [user1, user2]
        self.user_mapping.alchemy_to_sdm.side_effect = sdm_users
        result = self._userManager.get_all_users()
        self.assertEquals(result, sdm_users)
        user_dao.get_all.assert_called_once_with()  # @UndefinedVariable
        expected = [call(user1), call(user2)]
        self.user_mapping.alchemy_to_sdm.assert_has_calls(expected)  # @UndefinedVariable

    def test_get_user(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user_dao.get = Mock()
        user_dao.get.return_value = user1
        user1_sdm = UserSdm()
        self.user_mapping.alchemy_to_sdm.return_value = user1_sdm
        result = self._userManager.get_user(1)
        user_dao.get.assert_called_with(1)  # @UndefinedVariable
        self.user_mapping.alchemy_to_sdm.assert_called_with(user1)
        self.assertEqual(result, user1_sdm)

    def test_get_non_existing_user(self):
        def mock_get(userid):
            raise LookupError()

        user_dao.get = Mock()
        user_dao.get.side_effect = mock_get
        self.assertRaises(NoSuchElementException, self._userManager.get_user, 1)
        user_dao.get.assert_called_with(1)  # @UndefinedVariable
        user_dao.get.side_effect = None

    def test_create_user(self):
        user_sdm = UserSdm()
        user1 = UserFeatures()
        user1.firstname = 'test1'
        self.user_mapping.sdm_to_alchemy.return_value = user1
        user_dao.add_user = Mock()
        self._userManager.create_user(user_sdm)
        user_dao.add_user.assert_called_with(user1)  # @UndefinedVariable
        self.user_mapping.sdm_to_alchemy.assert_called_with(user_sdm)

    def test_edit_user_without_voicemail(self):
        data = {'firstname': 'Robert',
                'lastname': 'Dupond',
                'ctiprofileid': 1}
        intern_data = copy.deepcopy(data)
        intern_data['cti_profile_id'] = 1
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        user_dao.get.return_value = UserFeatures(firstname='Robert', lastname='Dupond')
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)  # @UndefinedVariable
        user_dao.get.assert_called_with(1)  # @UndefinedVariable
        self.assertFalse(self.voicemail_manager.edit_voicemail.called)
        self.user_mapping.sdm_to_alchemy_dict.assert_called_with(data)

    def test_edit_user_with_voicemail(self):
        data = {'firstname': 'Robert',
                'lastname': 'Dupond',
                'ctiprofileid': 1}
        intern_data = copy.deepcopy(data)
        intern_data['cti_profile_id'] = 1
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        user_dao.get.return_value = UserFeatures(firstname='Robert',
                                                 lastname='Dupond',
                                                 voicemailid=2)
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)  # @UndefinedVariable
        user_dao.get.assert_called_with(1)  # @UndefinedVariable
        self.voicemail_manager.edit_voicemail.assert_called_with(2, {'fullname': 'Robert Dupond'})
        self.user_mapping.sdm_to_alchemy_dict.assert_called_with(data)

    def test_edit_user_voicemail_update_not_needed(self):
        data = {'description': 'a short description',
                'ctiprofileid': 1}
        intern_data = copy.deepcopy(data)
        intern_data['cti_profile_id'] = 1
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)  # @UndefinedVariable
        self.assertFalse(user_dao.get.called)  # @UndefinedVariable
        self.assertFalse(self.voicemail_manager.edit_voicemail.called)

    def test_edit_user_not_found(self):
        data = {'lastname': 'test'}
        user_dao.update = Mock()
        user_dao.update.return_value = 0
        self.assertRaises(NoSuchElementException, self._userManager.edit_user,
                          1, data)
