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

from flask import Blueprint
from flask_rest import RESTResource
from tests.test_config import TestConfig

api = Blueprint("api", __name__, url_prefix=TestConfig.XIVO_REST_SERVICE_ROOT_PATH)


class RestHttpServer(object):


    def __init__(self):
        pass


    def add(self):
#        print("rest_id: " + rest_id + " data: " + data)
        return 201, "nic"
#        return 400, form.errors


    def get(self, rest_id):
        print("rest_id: " + rest_id)
        return 200, ("Rest response, rest_id: " + rest_id)


    def delete(self, rest_id):
        print("rest_id: " + rest_id)
        return 200, "DELETED"


    def update(self, rest_id, data):
        print("rest_id: " + rest_id + " data: " + data)
        return 200, "UPDATED"
#        return 400, form.errors

    def list(self):
        return "List to be implemented"


project_resource = RESTResource(
    name="rest",
    inject_name="data",
    route=TestConfig.XIVO_RECORDING_SERVICE_PATH,
    app=api,
    actions=["add", "update", "delete", "get", "list"],
    handler=RestHttpServer())

# name, route, app, handler, authentifier=None, actions=None, inject_name=None):
#        """
#        :name:
#            name of the resource. This is being used when registering
#            the route, for its name and for the name of the id parameter
#            that will be passed to the views
#
#        :route:
#           Default route for this resource
#
#        :app:
#            Application to register the routes onto
#
#        :actions:
#            Authorized actions. Optional. None means all.
#
#        :handler:
#            The handler instance which will handle the requests
#
#        :authentifier:
#            callable checking the authentication. If specified, all the
#            methods will be checked against it.


