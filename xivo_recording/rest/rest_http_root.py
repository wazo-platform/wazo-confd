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

import logging
from flask import Blueprint
from flask import request
from flask_rest import RESTResource
from recording_config import RecordingConfig
import cti_encoder
from services import campagne_management

root = Blueprint("root", __name__, url_prefix=RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH)

logger = logging.getLogger(__name__)


class RestHttpServerRoot(object):

    def __init__(self):
        self._campagne_manager = campagne_management.campagne_manager

    def add(self):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, root add, body: " + str(body) + " args: " + str(request.args))

    def get(self):
        return 501, ("Work in progress, root get, args: " + str(request.args))

    def delete(self):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, root delete, body: " + str(body) + " args: " + str(request.args))

    def update(self):
        try:
            body = cti_encoder.decode(request.data)
        except ValueError:
            body = "No parsable data in the request"
        return 501, ("Work in progress, root update, body: " + str(body) + " args: " + str(request.args))

    def list(self):
        result = self._campagne_manager.get_campagnes_as_dict()
        return 200, (cti_encoder.encode(result))

project_resource = RESTResource(
    name="rest",
    route=RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/",
    app=root,
    actions=["add", "update", "delete", "get", "list"],
    handler=RestHttpServerRoot())
