# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask.globals import request
from flask.helpers import make_response
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.rest.helpers import users_helper
from xivo_restapi.rest.negotiate.flask_negotiate import produces, consumes
from xivo_restapi.services.user_management import UserManagement
import logging

logger = logging.getLogger(__name__)


class APIUsers:

    def __init__(self):
        self._user_management = UserManagement()

    @produces('application/json')
    @realmDigest.requires_auth
    def list(self):
        logger.info("Got a GET request for users (list)")
        try:
            result = self._user_management.get_all_users()
            result = {"items": result}
            result = rest_encoder.encode(result)
            return make_response(result,
                                 200)
        except Exception as e:
            result = rest_encoder.encode([str(e)])
            return make_response(result, 500)

    @produces('application/json')
    @realmDigest.requires_auth
    def get(self, userid):
        logger.info("Got a GET request for users (get)")
        try:
            result = self._user_management.get_user(int(userid))
            result = rest_encoder.encode(result)
            return make_response(result, 200)
        except Exception as e:
            result = rest_encoder.encode([str(e)])
            return make_response(result, 500)

    @consumes('application/json')
    @produces('application/json')
    @realmDigest.requires_auth
    def create(self):
        logger.info("Got a POST request for users")
        try:
            data = rest_encoder.decode(request.data)
        except ValueError:
            response = rest_encoder.encode(["No parsable data in the request"])
            return make_response(response, 400)
        try:
            user = users_helper.create_instance(data)
            self._user_management.create_user(user)
            return make_response(None, 201)
        except Exception as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 500)
