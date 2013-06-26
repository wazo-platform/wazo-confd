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
from xivo_restapi.v1_0.mapping_alchemy_sdm.abstract_mapping import AbstractMapping


class VoicemailMapping(AbstractMapping):
    # mapping = {alchemy_field: sdm_field}
    mapping = {'uniqueid': 'id',
               'email': 'email',
               'fullname': 'fullname',
               'mailbox': 'mailbox',
               'password': 'password',
               'attach': 'attach',
               'skipcheckpass': 'skipcheckpass',
               'deletevoicemail': 'deleteaftersend'
               }

    reverse_mapping = dict((v, k) for k, v in mapping.items())

    alchemy_default_values = {'context': 'default',
                              'tz': 'eu-fr'}

    alchemy_types = {
                       'attach': int,
                       'skipcheckpass': int,
                       'deletevoicemail': int
                     }

    sdm_types = {
                'attach': bool,
                'skipcheckpass': bool,
                'deleteaftersend': bool
                 }

    def __init__(self):
        self.sdm_class = VoicemailSdm
        self.alchemy_class = Voicemail
