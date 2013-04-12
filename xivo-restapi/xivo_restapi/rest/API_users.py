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
from xivo_dao.service_data_model.sdm_exception import \
    IncorrectParametersException
from xivo_dao.service_data_model.user_sdm import UserSdm
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.rest.helpers import global_helper
from xivo_restapi.rest.negotiate.flask_negotiate import produces, consumes
from xivo_restapi.services.user_management import UserManagement
from xivo_restapi.services.utils.exceptions import NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class APIUsers:

    def __init__(self):
        self._user_management = UserManagement()
        self._user_sdm = UserSdm()

    @produces('application/json')
    @realmDigest.requires_auth
    def list(self):
        logger.info("List of users requested.")
        try:
            result = self._user_management.get_all_users()
            result = {"items": result}
            result = rest_encoder.encode(result)
            return make_response(result, 200)
        except Exception as e:
            result = rest_encoder.encode([str(e)])
            return make_response(result, 500)

    @produces('application/json')
    @realmDigest.requires_auth
    def get(self, userid):
        logger.info("User of id %s requested" % userid)
        try:
            result = self._user_management.get_user(int(userid))
            result = rest_encoder.encode(result)
            return make_response(result, 200)
        except NoSuchElementException:
            return make_response('', 404)
        except Exception as e:
            result = rest_encoder.encode([str(e)])
            return make_response(result, 500)

    @consumes('application/json')
    @realmDigest.requires_auth
    def create(self):
        data = request.data.decode("utf-8")
        logger.info("Request for creating a user with data: %s" % data)
        try:
            data = rest_encoder.decode(data)
        except ValueError:
            response = rest_encoder.encode(["No parsable data in the request"])
            return make_response(response, 400)
        try:
            self._user_sdm.validate(data)
            user = global_helper.create_class_instance(UserSdm, data)
            self._user_management.create_user(user)
            return make_response('', 201)
        except IncorrectParametersException as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 400)
        except Exception as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 500)

    @consumes('application/json')
    @realmDigest.requires_auth
    def edit(self, userid):
        data = request.data.decode("utf-8")
        logger.info("Request for editing the user of id %s with data %s ."
                    % (userid, data))
        try:
            data = rest_encoder.decode(data)
        except ValueError:
            response = rest_encoder.encode(["No parsable data in the request"])
            return make_response(response, 400)
        try:
            self._user_sdm.validate(data)
            self._user_management.edit_user(int(userid), data)
            return make_response('', 200)
        except IncorrectParametersException as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 400)
        except NoSuchElementException:
            return make_response('', 404)
        except Exception as e:
            data = rest_encoder.encode([str(e)])
            return make_response(data, 500)

    @realmDigest.requires_auth
    def delete(self, userid):
        try:
            self._user_management.delete_user(int(userid))
            return make_response('', 200)
        except NoSuchElementException:
            return make_response('', 404)
