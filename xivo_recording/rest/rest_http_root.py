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

from flask import Blueprint, request
from flask.helpers import make_response
import rest_encoder
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.services.campagne_management import CampagneManagement
import logging

logger = logging.getLogger(__name__)

root = Blueprint("root",
                 __name__,
                 url_prefix=RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                            RecordingConfig.XIVO_RECORDING_SERVICE_PATH)


class RestHttpServerRoot(object):

    def __init__(self):
        self._campagne_manager = CampagneManagement()

    def add(self):
        try:
            body = rest_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request, data: " + request.data
            return make_response(body, 400)

        result = self._campagne_manager.create_campaign(body)
        if (result == True):
            return make_response(("Added: " + str(result)), 201)
        else:
            return make_response(str(result), 500)

    def get(self, resource_id):
        return make_response(("Work in progress, root get, resource_id: " + str(resource_id) +
                              " args: " + str(request.args)),
                              501)

    def delete(self, resource_id):
        try:
            body = rest_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return make_response(("Work in progress, root delete, resource_id: " + str(resource_id) +
                              " body: " + str(body) +
                              " args: " + str(request.args)),
                             501)

    def update(self, resource_id):
        try:
            body = rest_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return make_response(("Work in progress, root update, resource_id: " + str(resource_id) +
                              " body: " + str(body) +
                              " args: " + str(request.args)),
                             501)

    def list(self):
        logger.debug("entering list")
        try:
            result = self._campagne_manager.get_campaigns_as_dict()
            logger.debug("got result")
            body = rest_encoder.encode(result)
            logger.debug("result encoded")
            return make_response(body, 200)
        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            return make_response(e.args, 500)


root.add_url_rule("/",
                  "list",
                  getattr(RestHttpServerRoot(), "list"),
                  methods=["GET"])

root.add_url_rule("/<resource_id>",
                  "get",
                  getattr(RestHttpServerRoot(), "get"),
                  methods=["GET"])

root.add_url_rule('/',
                  'add',
                  getattr(RestHttpServerRoot(), "add"),
                  methods=['POST'])

root.add_url_rule('/<resource_id>',
                  'update',
                  getattr(RestHttpServerRoot(), "update"),
                  methods=['PUT'])

root.add_url_rule('/<resource_id>',
                  'delete',
                  getattr(RestHttpServerRoot(), "delete"),
                  methods=['DELETE'])
