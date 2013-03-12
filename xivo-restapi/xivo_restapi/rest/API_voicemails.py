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
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers.voicemails_helper import VoicemailsHelper
from xivo_restapi.rest.negotiate.flask_negotiate import produces, consumes
from xivo_restapi.services.utils.exceptions import NoSuchElementException, \
    IncorrectParametersException
from xivo_restapi.services.voicemail_management import VoicemailManagement
import logging

logger = logging.getLogger(__name__)


class APIVoicemails:

    def __init__(self):
        self.voicemail_manager = VoicemailManagement()
        self._voicemails_helper = VoicemailsHelper()

    @produces("application/json")
    def list(self):
        logger.info("List of voicemails requested.")
        try:
            voicemails = self.voicemail_manager.get_all_voicemails()
            result = {"items": voicemails}
            result = rest_encoder.encode(result)
            return make_response(result, 200)
        except Exception as e:
            result = rest_encoder.encode(str(e))
            return make_response(result, 500)

    @consumes("application/json")
    def edit(self, voicemailid):
        logger.info("Edit request for voicemail of id %s with data %s"
                    % (voicemailid, request.data))
        try:
            data = rest_encoder.decode(request.data)
        except ValueError:
            result = ["No parsable data in the request"]
            return make_response(rest_encoder.encode(result), 400)
        try:
            self._voicemails_helper.validate_data(data)
            self.voicemail_manager.edit_voicemail(int(voicemailid), data)
        except IncorrectParametersException as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 400)
        except NoSuchElementException:
            return make_response('', 404)
        return make_response('', 200)
