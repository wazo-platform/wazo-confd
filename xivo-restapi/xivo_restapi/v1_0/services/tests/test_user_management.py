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

import unittest

from hamcrest import assert_that, equal_to
from mock import Mock, call, patch
from provd.rest.client.client import DeviceManager, ConfigManager
from urllib2 import URLError
from xivo_dao import user_dao, line_dao, voicemail_dao
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_restapi.v1_0.service_data_model.line_sdm import LineSdm
from xivo_restapi.v1_0.service_data_model.user_sdm import UserSdm
from xivo_restapi.v1_0.services.user_management import UserManagement
from xivo_restapi.v1_0.services.utils.exceptions import NoSuchElementException, \
    ProvdError, VoicemailExistsException, SysconfdError
from xivo_restapi.v1_0.services.utils.sysconfd_connector import SysconfdConnector
from xivo_restapi.v1_0.services.voicemail_management import VoicemailManagement
from xivo_restapi.v1_0.mapping_alchemy_sdm.line_mapping import LineMapping
from xivo_restapi.v1_0.mapping_alchemy_sdm.user_mapping import UserMapping
from xivo_dao.data_handler.device.model import Device


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
        self.sysconfd_connector = Mock(SysconfdConnector)
        self._userManager.sysconfd_connector = self.sysconfd_connector
        self._generate_test_data()

    def _generate_test_data(self):
        self.deviceid = "abcd"
        self.user = UserFeatures()
        self.user.id = 1
        self.line = LineFeatures()
        self.line.id = 2
        self.line.number = "2000"
        self.line.protocol = "sip"
        self.line.protocolid = 3
        self.line.context = "default"
        self.line.num = 4
        self.line.device = 123

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
        user_dao.get_all_join_line.assert_called_once_with()
        expected = [call(user1), call(user2)]
        self.user_mapping.alchemy_to_sdm.assert_has_calls(expected)
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
        user_dao.get_user_join_line.assert_called_with(1)
        self.user_mapping.alchemy_to_sdm.assert_called_with(user1)
        self.assertEqual(result, user1_sdm)
        self.assertEquals(result.line, line1_sdm)

    def test_get_non_existing_user(self):
        user_dao.get_user_join_line = Mock()
        user_dao.get_user_join_line.return_value = None
        self.assertRaises(NoSuchElementException, self._userManager.get_user, 1)
        user_dao.get_user_join_line.assert_called_with(1)

    def test_create_user(self):
        user_sdm = UserSdm()
        user1 = UserFeatures()
        user1.firstname = 'test1'
        self.user_mapping.sdm_to_alchemy.return_value = user1
        user_dao.add_user = Mock()
        self._userManager.create_user(user_sdm)
        user_dao.add_user.assert_called_with(user1)
        self.user_mapping.sdm_to_alchemy.assert_called_with(user_sdm)

    def test_edit_user_without_voicemail(self):
        data = {'firstname': 'Robert',
                'lastname': 'Dupond',
                'ctiprofileid': 1}
        intern_data = {'firstname': 'Robert',
                       'lastname': 'Dupond',
                       'cti_profile_id': 1}
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        user_dao.get.return_value = UserFeatures(firstname='Robert', lastname='Dupond')
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)
        user_dao.get.assert_called_with(1)
        self.assertFalse(self.voicemail_manager.edit_voicemail.called)
        self.user_mapping.sdm_to_alchemy_dict.assert_called_with(data)

    def test_edit_user_with_voicemail(self):
        data = {'firstname': 'Robert',
                'lastname': 'Dupond',
                'ctiprofileid': 1}
        intern_data = {'firstname': 'Robert',
                       'lastname': 'Dupond',
                       'cti_profile_id': 1}
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        user_dao.get.return_value = UserFeatures(firstname='Robert',
                                                 lastname='Dupond',
                                                 voicemailid=2)
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)
        user_dao.get.assert_called_with(1)
        self.voicemail_manager.edit_voicemail.assert_called_with(2, {'fullname': 'Robert Dupond'})
        self.user_mapping.sdm_to_alchemy_dict.assert_called_with(data)

    def test_edit_user_voicemail_update_not_needed(self):
        data = {'description': 'a short description',
                'ctiprofileid': 1}
        intern_data = {'description': 'a short description',
                       'cti_profile_id': 1}
        user_dao.update = Mock()
        user_dao.update.return_value = 1
        user_dao.get = Mock()
        self.user_mapping.sdm_to_alchemy_dict.return_value = intern_data
        self._userManager.edit_user(1, data)
        user_dao.update.assert_called_once_with(1, intern_data)
        self.assertFalse(user_dao.get.called)
        self.assertFalse(self.voicemail_manager.edit_voicemail.called)

    def test_edit_user_not_found(self):
        data = {'lastname': 'test'}
        user_dao.update = Mock()
        user_dao.update.return_value = 0
        self.assertRaises(NoSuchElementException, self._userManager.edit_user,
                          1, data)

    def test_provd_remove_line(self):
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"},
                    "2": {"username": "5678"}
                },
                "funckeys": {}
            }
        }
        self.config_manager.get.return_value = config_dict

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                },
                "funckeys": {}
            }
        }

        self._userManager._provd_remove_line(self.deviceid, 2)

        self.config_manager.get.assert_called_with(self.deviceid)
        self.config_manager.update.assert_called_with(expected_arg)
        self.assertEquals(0, self.config_manager.autocreate.call_count)

    def test_provd_remove_line_autoprov(self):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                },
                "funckeys": {}
            }
        }

        device_dict = {"ip": "10.60.0.109",
                       "version": "3.2.2.1136",
                       "config": self.deviceid,
                       "id": self.deviceid}
        self.config_manager.get.return_value = config_dict
        self.device_manager.get.return_value = device_dict
        self.config_manager.autocreate.return_value = autoprovid

        expected_arg_config = {"raw_config": {}}
        expected_arg_device = {"ip": "10.60.0.109",
                               "version": "3.2.2.1136",
                               "config": autoprovid,
                               "id": self.deviceid}
        self._userManager._provd_remove_line(self.deviceid, 1)

        self.config_manager.get.assert_called_with(self.deviceid)
        self.config_manager.autocreate.assert_called_with()
        self.device_manager.get.assert_called_with(self.deviceid)
        self.device_manager.update.assert_called_with(expected_arg_device)
        self.config_manager.update.assert_called_with(expected_arg_config)

    def test_provd_remove_line_no_funckeys(self):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "sip_lines": {
                    "1": {"username": "1234"}
                },
                "funckeys": {}
            }
        }
        device_dict = {"ip": "10.60.0.109",
                       "version": "3.2.2.1136",
                       "config": self.deviceid,
                       "id": self.deviceid}
        self.config_manager.get.return_value = config_dict
        self.device_manager.get.return_value = device_dict
        self.config_manager.autocreate.return_value = autoprovid

        try:
            self._userManager._provd_remove_line("abcd", 1)
        except:
            self.fail("An exception was raised whereas it should not")

    @patch('xivo_dao.data_handler.user.services.get')
    def test_delete_unexisting_user(self, mock_user_services):
        user_id = 1
        mock_user_services.side_effect = ElementNotExistsError('User', id=user_id)
        self.assertRaises(NoSuchElementException, self._userManager.delete_user, user_id)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_user(self, mock_user_delete, mock_user_get):
        userid = 1
        user = Mock()
        user.voicemail_id = None
        mock_user_get.return_value = user
        self._userManager._remove_lines = Mock()
        self._userManager._delete_voicemail = Mock()

        self._userManager.delete_user(userid)

        mock_user_get.assert_called_once_with(userid)
        mock_user_delete.assert_called_once_with(user)
        self._userManager._remove_lines.assert_called_with(user)
        assert_that(self._userManager._delete_voicemail.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_with_voicemail(self, mock_user_delete, mock_user_get):
        userid = 1
        user = Mock()
        user.voicemail_id = 12
        mock_user_get.return_value = user

        self.assertRaises(VoicemailExistsException, self._userManager.delete_user, userid)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_user_force_voicemail_deletion(self, mock_user_delete, mock_user_get):
        userid = 1
        user = Mock()
        user.voicemail_id = 17
        mock_user_get.return_value = user
        self._userManager._remove_lines = Mock()
        self._userManager._remove_voicemail = Mock()

        self._userManager.delete_user(userid, delete_voicemail=True)

        mock_user_get.assert_called_once_with(userid)
        mock_user_delete.assert_called_once_with(user)
        self._userManager._remove_lines.assert_called_with(user)
        self._userManager._remove_voicemail.assert_called_with(user, True)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id', Mock(return_value=[]))
    def test_remove_lines_no_lines(self):
        user = Mock()
        self._userManager._remove_association = Mock()

        self._userManager._remove_lines(user)

        assert_that(self._userManager._remove_association.call_count, equal_to(0))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_remove_lines_one_lines(self, mock_find_associations):
        user_id = 34
        user = Mock(id=user_id)
        ule = Mock()
        mock_find_associations.return_value = [ule]
        self._userManager._remove_association = Mock()

        self._userManager._remove_lines(user)

        mock_find_associations.assert_called_once_with(user_id)
        self._userManager._remove_association.assert_called_once_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.dao.delete')
    @patch('xivo_dao.line_dao.get')
    def test_remove_association(self,
                                mock_line_dao,
                                mock_ule_delete):
        user_id = 12
        line_id = 23
        extension_id = 43
        ule = Mock(user_id=user_id, line_id=line_id, extension_id=extension_id)
        line = Mock()
        mock_line_dao.return_value = line
        self._userManager._remove_line = Mock()

        self._userManager._remove_association(ule)

        mock_ule_delete.assert_called_once_with(ule)
        mock_line_dao.assert_called_once_with(line_id)
        self._userManager._remove_line.assert_any_call(line)

    @patch('xivo_dao.data_handler.device.services.get')
    def test_remove_line_provd_error(self, device_services_get):
        device = Device(id='1234')
        line_dao.delete = Mock()
        device_services_get.return_value = device
        self._userManager._provd_remove_line = Mock()
        self._userManager._provd_remove_line.side_effect = URLError("sample error")

        self.assertRaises(ProvdError, self._userManager._remove_line, self.line)

    def test_delete_voicemail(self):
        voicemail_dao.delete = Mock()
        voicemail = Voicemail(uniqueid=1, mailbox="123", context="default")
        voicemail_dao.get = Mock()
        voicemail_dao.get.return_value = voicemail

        self._userManager._delete_voicemail(1)
        voicemail_dao.delete.assert_called_with(1)
        self.sysconfd_connector.delete_voicemail_storage.assert_called_with("default", "123")

    def test_delete_voicemail_sysconfd_error(self):
        voicemail_dao.delete = Mock()
        voicemail = Voicemail(uniqueid=1, mailbox="123", context="default")
        voicemail_dao.get = Mock()
        voicemail_dao.get.return_value = voicemail
        self.sysconfd_connector.delete_voicemail_storage.side_effect = Exception

        self.assertRaises(SysconfdError, self._userManager._delete_voicemail, 1)
