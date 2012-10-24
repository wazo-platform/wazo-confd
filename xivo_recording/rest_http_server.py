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
from tests.test_config import TestConfig
from flask import request
from xivo_cti_encoding_interface.cti_encoder_provider import CtiEncoderProvider
from flask_rest import RESTResource

api = Blueprint("api", __name__, url_prefix=TestConfig.XIVO_REST_SERVICE_ROOT_PATH)

logger = logging.getLogger(__name__)


class RestHttpServer(object):

#    @api.route('/', methods=["POST"])
    def add(self, data):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 201, ("add, body: " + str(body) + " data: " + data + " args: " + str(request.args))
#        return 400, form.errors

#    @api.route('/', methods=["GET"])
    def get(self, rest_id):
        return 200, ("get, rest_id: " + rest_id + " args: " + str(request.args))

    def delete(self, rest_id, data):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("DELETED, rest_id" + rest_id + " body: " + str(body) + " args: " + str(request.args))

    def update(self, rest_id, data):
        logger.debug("PUT body: " + request.data)
        logger.debug("decode")
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("update, rest_id: " + rest_id + "body: " + str(body) + " args: " + str(request.args))

    def list(self, data):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("list, body: " + str(body) + " args: " + str(request.args))


project_resource = RESTResource(
    name="rest",
    inject_name="data",
    route=TestConfig.XIVO_RECORDING_SERVICE_PATH + "/<data>",
    app=api,
    actions=["add", "update", "delete", "get"],  #"add", "update", "delete", "get", "list"],
    handler=RestHttpServer())


class RestHttpServerRoot(object):

    def add(self):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 201, ("add, body: " + str(body) + " args: " + str(request.args))
#        return 400, form.errors

    def get(self, rest_id):
        return 200, ("get, rest_id: " + rest_id + " args: " + str(request.args))

    def delete(self, rest_id):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("DELETED, rest_id" + rest_id + " body: " + str(body) + " args: " + str(request.args))

    def update(self, rest_id):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("update, rest_id: " + rest_id + "body: " + str(body) + " args: " + str(request.args))

    def list(self):
        try:
            body = CtiEncoderProvider.encoder.decode(request.data)
        except ValueError:
            body = "No data in the request"
        return 200, ("list, body: " + str(body) + " args: " + str(request.args))

project_resource = RESTResource(
    name="rest",
    route=TestConfig.XIVO_RECORDING_SERVICE_PATH + "/",
    app=api,
    actions=["add", "update", "delete", "get"],  #"add", "update", "delete", "get", "list"],
    handler=RestHttpServerRoot())
