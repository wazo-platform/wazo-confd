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

from flask import request
from flask.helpers import make_response
import rest_encoder
from xivo_recording.services.recording_management import RecordingManagement
import logging


logger = logging.getLogger(__name__)


class APIRecordings(object):

    def __init__(self):
        self._recording_manager = RecordingManagement()

    def add_recording(self, campaign_id):
        try:
            body = rest_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request, data: " + request.data
            return make_response(body, 400)

        result = self._recording_manager.add_recording(campaign_id, body)
        if (result == True):
            return make_response(("Added: " + str(result)), 201)
        else:
            return make_response(str(result), 500)

    def list_recordings(self, campaign_id):
        try:
            logger.debug("List args:" + str(request.args))
            result = self._recording_manager. \
                        get_recordings_as_dict(campaign_id, request.args)

            logger.debug("got result")
            body = rest_encoder.encode(result)
            logger.debug("result encoded")
            return make_response(body, 200)

        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            return make_response(str(e.args), 500)
