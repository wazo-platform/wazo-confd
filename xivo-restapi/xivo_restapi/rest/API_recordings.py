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
from flask_negotiate import consumes, produces
from xivo_restapi.rest.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.rest.helpers import recordings_helper, global_helper
from xivo_restapi.services.recording_management import RecordingManagement
import logging
import rest_encoder


logger = logging.getLogger(__name__)


class APIRecordings(object):

    def __init__(self):
        self._recording_manager = RecordingManagement()

    @consumes('application/json')
    @produces('application/json')
    @realmDigest.requires_auth
    def add_recording(self, campaign_id):
        try:
            body = rest_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request, data: " + request.data
            return make_response(rest_encoder.encode(body), 400)
        body = recordings_helper.supplement_add_input(body)
        recording = recordings_helper.create_instance(body)
        if('agent_no' in body):
            recording.agent_no = body['agent_no']
        try:
            result = self._recording_manager.add_recording(campaign_id, recording)
        except Exception as e:
            body = "SQL Error: " + str(e.message)
            return make_response(rest_encoder.encode(body), 400)

        if (result):
            return make_response(rest_encoder.encode("Added: " + \
                                                     str(result)), 201)
        else:
            body = rest_encoder.encode([str(result)])
            return make_response(body, 500)

    @produces('application/json')
    @realmDigest.requires_auth
    def list_recordings(self, campaign_id):
        try:
            logger.debug("List args:" + str(request.args))
            params = {}
            for item in request.args:
                if(not item.startswith('_')):
                    params[item] = request.args[item]
            paginator = global_helper.create_paginator(request.args)
            result = self._recording_manager.get_recordings(campaign_id,
                                                            params,
                                                            paginator)

            logger.debug("got result")
            body = rest_encoder.encode(result)
            logger.debug("result encoded")
            return make_response(body, 200)

        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            body = rest_encoder.encode([str(e.args)])
            return make_response(body, 500)

    @produces('application/json')
    @realmDigest.requires_auth
    def search(self, campaign_id):
        try:
            logger.debug("List args:" + str(request.args))
            params = {}
            for item in request.args:
                if(not item.startswith('_')):
                    params[item] = request.args[item]
            paginator = global_helper.create_paginator(request.args)
            result = self._recording_manager. \
                        search_recordings(campaign_id, params,
                                          paginator)

            logger.debug("got result")
            body = rest_encoder.encode(result)
            logger.debug("result encoded")
            return make_response(body, 200)
        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            body = rest_encoder.encode([str(e.args)])
            return make_response(body, 500)

    @produces('application/json')
    @realmDigest.requires_auth
    def delete(self, campaign_id, recording_id):
        try:
            logger.debug("Entering delete:" + str(campaign_id) + ", " + \
                         str(recording_id))
            result = self._recording_manager. \
                        delete(campaign_id, recording_id)
            logger.debug("result encoded")
            if not result:
                return make_response(rest_encoder.encode("No such recording"),
                                     404)
            else:
                return make_response(rest_encoder.encode("Deleted: True"), 200)
        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            body = rest_encoder.encode([str(e.args)])
            return make_response(body, 500)
