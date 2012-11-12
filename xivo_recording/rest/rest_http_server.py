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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import logging
from flask import Blueprint
from flask import request
from flask_rest import RESTResource
from recording_config import RecordingConfig
import cti_encoder
from services.campagne_management import CampagneManagement

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__, url_prefix=RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH)


class RestHttpServer(object):

    def __init__(self):
        self._campagne_manager = CampagneManagement()

    def add(self, data):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request, data: " + request.data
            return 400, body

        result = self._campagne_manager.create_campagne(body)
        if (result == True):
            return 201, ("Added: " + str(result))
        else:
            return 500, str(result)

    def get(self, rest_id):
        return 501, ("Work in progress, get, rest_id: " + rest_id + " args: " + str(request.args))

    def delete(self, rest_id, data):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, DELETED, rest_id" + rest_id + " body: " + str(body) + " args: " + str(request.args))

    def update(self, rest_id, data):
        logger.debug("PUT body: " + request.data)
        logger.debug("decode")
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, update, rest_id: " + rest_id + "body: " + str(body) + " args: " + str(request.args))

    def list(self, data):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, list, body: " + str(body) + " args: " + str(request.args))


project_resource = RESTResource(
    name="rest",
    inject_name="data",
    route=RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/<data>",
    app=api,
    actions=["add", "update", "delete", "get", "list"],
    handler=RestHttpServer())
