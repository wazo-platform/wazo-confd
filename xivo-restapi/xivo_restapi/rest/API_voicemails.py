# -*- coding: UTF-8 -*-

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

from flask.globals import request
from flask.helpers import make_response
from xivo_dao.service_data_model.sdm_exception import \
    IncorrectParametersException
from xivo_dao.service_data_model.voicemail_sdm import VoicemailSdm
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.rest.negotiate.flask_negotiate import produces, consumes
from xivo_restapi.services.voicemail_management import VoicemailManagement
import logging
from xivo_restapi.rest.helpers.global_helper import exception_catcher

logger = logging.getLogger(__name__)


class APIVoicemails(object):

    def __init__(self):
        self.voicemail_manager = VoicemailManagement()
        self.voicemail_sdm = VoicemailSdm()

    @exception_catcher
    @produces("application/json")
    @realmDigest.requires_auth
    def list(self):
        logger.info("List of voicemails requested.")
        voicemails = self.voicemail_manager.get_all_voicemails()
        result = {"items": voicemails}
        result = rest_encoder.encode(result)
        return make_response(result, 200)

    @exception_catcher
    @consumes("application/json")
    @realmDigest.requires_auth
    def edit(self, voicemailid):
        data = request.data.decode("utf-8")
        logger.info("Edit request for voicemail of id %s with data %s"
                    % (voicemailid, data))

        data = rest_encoder.decode(data)
        try:
            self.voicemail_sdm.validate(data)
            self.voicemail_manager.edit_voicemail(int(voicemailid), data)
        except IncorrectParametersException as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 400)
        return make_response('', 200)
