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
from provd.rest.client.client import DeviceManager, ConfigManager
from xivo_dao import user_dao, line_dao, usersip_dao, extensions_dao, \
    extenumber_dao, contextnummember_dao, device_dao
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.mapping_alchemy_sdm.line_mapping import LineMapping
from xivo_dao.mapping_alchemy_sdm.user_mapping import UserMapping
from xivo_dao.service_data_model.line_sdm import LineSdm
from xivo_dao.service_data_model.user_sdm import UserSdm
from xivo_restapi.services.user_management import UserManagement
from xivo_restapi.services.utils.exceptions import NoSuchElementException
from xivo_restapi.services.voicemail_management import VoicemailManagement
import copy
import unittest


class TestUserManagement(unittest.TestCase):

    def setUp(self):
        self._userManager = UserManagement()
        self.user_mapping = Mock(UserMapping)
        self._userManager.user_mapping = self.user_mapping
        self.voicemail_manager = Mock(VoicemailManagement)
        self._userManager.voicemail_manager = self.voicemail_manager
        self.line_mapping = Mock(LineMapping)
        self._userManager.line_mapping = self.line_mapping
        self.device_manager = Mock(DeviceManager)
        self._userManager.device_manager = self.device_manager
        self.config_manager = Mock(ConfigManager)
        self._userManager.config_manager = self.config_manager
        self.deviceid = "abcd"
        self.config_dict = {"raw_config":
                         {"sip_lines":
                           {"1":
                            {"username": "1234"},
                            "2":
                            {"username": "5678"}
                           },
                          "funckeys": {}
                          }
                        }
        self.device_dict = {"ip": "10.60.0.109",
                       "version":"3.2.2.1136",
                       "config": self.deviceid,
                       "id": self.deviceid}

    def test_get_all_users(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user1.cti_profile_id = 1
        user2 = UserFeatures()
        user2.firstname = 'test2'
        line1 = LineFeatures()
        line1.number = "123"
        line2 = LineFeatures()
        line2.number = "456"
        user_sdm1 = UserSdm()
        user_sdm2 = UserSdm()
        sdm_users = [user_sdm1, user_sdm2]

        line_sdm1 = LineSdm()
        line_sdm1.number = line1.number
        line_sdm2 = LineSdm()
        line_sdm2.number = line2.number
        user_dao.get_all_join_line = Mock()
        user_dao.get_all_join_line.return_value = [(user1, line1), (user2, line2)]
        self.user_mapping.alchemy_to_sdm.side_effect = sdm_users
        self.line_mapping.alchemy_to_sdm.side_effect = [line_sdm1, line_sdm2]

        result = self._userManager.get_all_users()
        self.assertEquals(result, sdm_users)
        user_dao.get_all_join_line.assert_called_once_with()  # @UndefinedVariable
        expected = [call(user1), call(user2)]
        self.user_mapping.alchemy_to_sdm.assert_has_calls(expected)  # @UndefinedVariable
        expected = [call(line1), call(line2)]
        self.line_mapping.alchemy_to_sdm.assert_has_calls(expected)
        self.assertEqual(user_sdm1.line.number, "123")
        self.assertEqual(user_sdm2.line.number, "456")

    def test_get_user(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        line1 = LineFeatures()
        line1.number = "1234"
        user_dao.get_user_join_line = Mock()
        user_dao.get_user_join_line.return_value = user1, line1
        user1_sdm = UserSdm()
        line1_sdm = LineSdm()
        self.user_mapping.alchemy_to_sdm.return_value = user1_sdm
        self.line_mapping.alchemy_to_sdm.return_value = line1_sdm

        result = self._userManager.get_user(1)
        user_dao.get_user_join_line.assert_called_with(1)  # @UndefinedVariable
        self.user_mapping.alchemy_to_sdm.assert_called_with(user1)
        self.assertEqual(result, user1_sdm)
        self.assertEquals(result.line, line1_sdm)

    def test_get_non_existing_user(self):
        user_dao.get_user_join_line = Mock()
        user_dao.get_user_join_line.return_value = None
        self.assertRaises(NoSuchElementException, self._userManager.get_user, 1)
        user_dao.get_user_join_line.assert_called_with(1)  # @UndefinedVariable

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

    def test_delete_user(self):
        user = UserFeatures()
        user.id = 1
        user_dao.get = Mock()
        user_dao.get.return_value = user
        line = LineFeatures()
        line.id = 2
        line.number = "2000"
        line.protocol = "sip"
        line.protocolid = 3
        line.context = "default"
        line.num = 4
        line.device = 123
        line_dao.find_line_id_by_user_id = Mock()
        line_dao.find_line_id_by_user_id.return_value = [2]
        line_dao.get = Mock()
        line_dao.get.return_value = line

        user_dao.delete = Mock()
        line_dao.delete = Mock()
        usersip_dao.delete = Mock()
        extensions_dao.delete_by_exten = Mock()
        extenumber_dao.delete_by_exten = Mock()
        contextnummember_dao.delete_by_userid_context = Mock()
        device_dao.get_deviceid = Mock()
        device_dao.get_deviceid.return_value = "abcdef"
        self._userManager.provd_remove_line = Mock()

        self._userManager.delete_user(1)
        user_dao.get.assert_called_with(1) # @UndefinedVariable
        line_dao.find_line_id_by_user_id.assert_called_with(1) # @UndefinedVariable
        line_dao.get.assert_called_with(2) # @UndefinedVariable
        user_dao.delete.assert_called_with(1) # @UndefinedVariable
        line_dao.delete.assert_called_with(2) # @UndefinedVariable
        usersip_dao.delete.assert_called_with(3) # @UndefinedVariable
        extensions_dao.delete_by_exten.assert_called_with("2000") # @UndefinedVariable
        extenumber_dao.delete_by_exten.assert_called_with("2000") # @UndefinedVariable
        contextnummember_dao.delete_by_userid_context.assert_called_with(1, "default") # @UndefinedVariable
        device_dao.get_deviceid.assert_called_with(123) # @UndefinedVariable
        self._userManager.provd_remove_line.assert_called_with("abcdef", 4)

    def test_provd_remove_line(self):
        self.config_manager.get.return_value = self.config_dict

        expected_arg = copy.deepcopy(self.config_dict)
        del expected_arg["raw_config"]["sip_lines"]["2"]
        self._userManager.provd_remove_line(self.deviceid, 2)

        self.config_manager.get.assert_called_with(self.deviceid)
        self.config_manager.update.assert_called_with(expected_arg)
        self.assertEquals(0, self.config_manager.autocreate.call_count)

    def test_provd_remove_line_autoprov(self):
        autoprovid = "autoprov1234"
        del self.config_dict["raw_config"]["sip_lines"]["2"]
        self.config_manager.get.return_value = self.config_dict
        self.device_manager.get.return_value = self.device_dict
        self.config_manager.autocreate.return_value = autoprovid

        expected_arg_config = copy.deepcopy(self.config_dict)
        del expected_arg_config["raw_config"]["sip_lines"]
        del expected_arg_config["raw_config"]["funckeys"]
        expected_arg_device = copy.deepcopy(self.device_dict)
        expected_arg_device["config"] = autoprovid
        self._userManager.provd_remove_line(self.deviceid, 1)

        self.config_manager.get.assert_called_with(self.deviceid)
        self.config_manager.autocreate.assert_called_with()
        self.device_manager.get.assert_called_with(self.deviceid)
        self.device_manager.update.assert_called_with(expected_arg_device)
        self.config_manager.update.assert_called_with(expected_arg_config)

    def test_provd_remove_line_no_funckeys(self):
        autoprovid = "autoprov1234"
        del self.config_dict["raw_config"]["sip_lines"]["2"]
        self.config_manager.get.return_value = self.config_dict
        self.device_manager.get.return_value = self.device_dict
        self.config_manager.autocreate.return_value = autoprovid

        try:
            self._userManager.provd_remove_line("abcd", 1)
            self.assertTrue(True)
        except:
            self.assertTrue(False, "An exception was raised whereas it should not")

    def test_delete_unexisting_user(self):
        def mock_get(userid):
            raise LookupError()

        user_dao.get = Mock()
        user_dao.get.side_effect = mock_get

        self.assertRaises(NoSuchElementException, self._userManager.delete_user, 1)
