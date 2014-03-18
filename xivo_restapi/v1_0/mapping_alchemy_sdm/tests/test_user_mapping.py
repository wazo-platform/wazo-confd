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
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.v1_0.service_data_model.user_sdm import UserSdm
import unittest
from xivo_restapi.v1_0.mapping_alchemy_sdm.user_mapping import UserMapping


class TestUserMapping(unittest.TestCase):

    def setUp(self):
        user_alchemy = UserFeatures()
        user_sdm = UserSdm()
        user_sdm.id = user_alchemy.id = None
        user_sdm.firstname = user_alchemy.firstname = "John"
        user_sdm.lastname = user_alchemy.lastname = "Doe"
        user_sdm.callerid = user_alchemy.callerid = "123"
        user_sdm.username = user_alchemy.loginclient = "john"
        user_sdm.password = user_alchemy.passwdclient = "123"
        user_sdm.enableclient = user_alchemy.enableclient = False
        user_sdm.musiconhold = user_alchemy.musiconhold = "my_music"
        user_sdm.outcallerid = user_alchemy.outcallerid = "456"
        user_sdm.mobilephonenumber = user_alchemy.mobilephonenumber = "06123123123"
        user_sdm.userfield = user_alchemy.userfield = "abc"
        user_sdm.timezone = user_alchemy.timezone = "Europe/France"
        user_sdm.language = user_alchemy.language = "fr_FR"
        user_sdm.description = user_alchemy.description = "sample user"
        user_sdm.ctiprofileid = user_alchemy.cti_profile_id = None
        user_sdm.voicemailid = user_alchemy.voicemailid = None
        user_sdm.agentid = user_alchemy.agentid = None
        user_sdm.entityid = user_alchemy.entityid = None

        self.user_alchemy = user_alchemy
        self.user_sdm = user_sdm

        self.user_mapping = UserMapping()

    def test_alchemy_to_sdm(self):
        result = self.user_mapping.alchemy_to_sdm(self.user_alchemy)
        self.assertEquals(self.user_sdm.__dict__, result.__dict__)

    def test_sdm_to_alchemy(self):
        self.user_alchemy.enableclient = 0
        self.user_alchemy.ringintern = ''
        self.user_alchemy.ringextern = ''
        self.user_alchemy.ringgroup = ''
        self.user_alchemy.ringforward = ''
        self.user_alchemy.rightcallcode = ''

        result = self.user_mapping.sdm_to_alchemy(self.user_sdm)

        self.assertEquals(self.user_alchemy.todict(), result.todict())

    def test_sdm_to_alchemy_dict(self):
        user_dict_sdm = {}
        user_dict_alchemy = {}
        firstname = "John"
        enableclient = True
        passwdclient = "supercesret"
        user_dict_alchemy['firstname'] = firstname
        user_dict_sdm['firstname'] = firstname
        user_dict_alchemy['enableclient'] = int(enableclient)
        user_dict_sdm['enableclient'] = enableclient
        user_dict_alchemy['passwdclient'] = passwdclient
        user_dict_sdm['password'] = passwdclient

        result = self.user_mapping.sdm_to_alchemy_dict(user_dict_sdm)
        self.assertEquals(user_dict_alchemy, result)
        self.assertEquals(type(user_dict_alchemy['enableclient']), type(result['enableclient']))

    def test_sdm_to_alchemy_dict_fails(self):
        user_dict_sdm = {}
        firstname = "John"
        deletevoicemail = True
        user_dict_sdm['firstname'] = firstname
        user_dict_sdm['notExistingKey'] = deletevoicemail

        self.assertRaises(AttributeError, self.user_mapping.sdm_to_alchemy_dict, user_dict_sdm)
