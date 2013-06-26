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

import logging

from xivo_dao import voicemail_dao
from xivo_restapi import config
from xivo_restapi.v1_0.mapping_alchemy_sdm.voicemail_mapping import VoicemailMapping
from xivo_restapi.v1_0.services.utils.exceptions import NoSuchElementException

data_access_logger = logging.getLogger(config.DATA_ACCESS_LOGGERNAME)


class VoicemailManagement(object):

    def __init__(self):
        self.voicemail_mapping = VoicemailMapping()

    def get_all_voicemails(self):
        list_voicemails_alchemy = voicemail_dao.all()
        list_voicemails_sdm = []
        for voicemail_alchemy in list_voicemails_alchemy:
            list_voicemails_sdm.append(self.voicemail_mapping.alchemy_to_sdm(voicemail_alchemy))
        return list_voicemails_sdm

    def edit_voicemail(self, voicemailid, data):
        data_access_logger.info("Editing the voicemail of id %d with data %s."
                                % (voicemailid, data))

        if voicemail_dao.get(voicemailid) is None:
            raise NoSuchElementException("No such voicemail: %s" % voicemailid)

        converted_data = self.voicemail_mapping.sdm_to_alchemy_dict(data)
        voicemail_dao.update(voicemailid, converted_data)
