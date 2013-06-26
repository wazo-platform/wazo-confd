# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_restapi.v1_0.service_data_model.voicemail_sdm import VoicemailSdm
import unittest
from xivo_restapi.v1_0.mapping_alchemy_sdm.voicemail_mapping import VoicemailMapping


class TestVoicemailMapping(unittest.TestCase):

    def setUp(self):
        voicemail_alchemy = Voicemail()
        voicemail_sdm = VoicemailSdm()
        voicemail_alchemy.uniqueid = voicemail_sdm.id = 1
        voicemail_alchemy.email = voicemail_sdm.email = "test@xivo.org"
        voicemail_alchemy.fullname = voicemail_sdm.fullname = "John doe sdf &é'é- "
        voicemail_alchemy.mailbox = voicemail_sdm.mailbox = "123@default.com"
        voicemail_alchemy.password = voicemail_sdm.password = "delamortqui tue"
        voicemail_alchemy.attach = 0
        voicemail_sdm.attach = False
        voicemail_alchemy.skipcheckpass = 1
        voicemail_sdm.skipcheckpass = True
        voicemail_alchemy.deletevoicemail = 1
        voicemail_sdm.deleteaftersend = True
        voicemail_alchemy.context = "default"
        voicemail_alchemy.tz = "eu-fr"

        self.voicemail_alchemy = voicemail_alchemy
        self.voicemail_sdm = voicemail_sdm
        self.voicemail_mapping = VoicemailMapping()

    def test_alchemy_to_sdm(self):
        result = self.voicemail_mapping.alchemy_to_sdm(self.voicemail_alchemy)
        self.assertEquals(self.voicemail_sdm.__dict__, result.__dict__)
        self.assertEquals(type(self.voicemail_sdm.deleteaftersend),
                          type(result.deleteaftersend))
        self.assertEquals(type(self.voicemail_sdm.skipcheckpass),
                          type(result.skipcheckpass))
        self.assertEquals(type(self.voicemail_sdm.attach),
                          type(result.attach))

    def test_sdm_to_alchemy(self):
        result = self.voicemail_mapping.sdm_to_alchemy(self.voicemail_sdm)
        self.assertEquals(self.voicemail_alchemy.todict(), result.todict())

    def test_sdm_to_alchemy_dict(self):
        voicemail_dict_sdm = {}
        voicemail_dict_alchemy = {}
        fullname = "John doe sdf &é'é- "
        deletevoicemail = True
        voicemail_dict_alchemy['fullname'] = fullname
        voicemail_dict_sdm['fullname'] = fullname
        voicemail_dict_alchemy['deletevoicemail'] = int(deletevoicemail)
        voicemail_dict_sdm['deleteaftersend'] = deletevoicemail

        result = self.voicemail_mapping.sdm_to_alchemy_dict(voicemail_dict_sdm)
        self.assertEquals(voicemail_dict_alchemy, result)
        self.assertEquals(type(voicemail_dict_alchemy['deletevoicemail']), type(result['deletevoicemail']))

    def test_sdm_to_alchemy_dict_fails(self):
        voicemail_dict_sdm = {}
        fullname = "John doe sdf &é'é- "
        deletevoicemail = True
        voicemail_dict_sdm['fullname'] = fullname
        voicemail_dict_sdm['notExistingKey'] = deletevoicemail

        self.assertRaises(AttributeError, self.voicemail_mapping.sdm_to_alchemy_dict, voicemail_dict_sdm)






