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

from acceptance.features.steps.helpers.ws_utils import WsUtils
from xivo_dao import user_dao
from xivo_restapi.restapi_config import RestAPIConfig
import random


class RestUsers():

    def __init__(self):
        self.ws_utils = WsUtils()

    def get_all_users(self):
        return self.ws_utils.rest_get(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/")

    def id_from_fullname(self, fullname):
        (firstname, lastname) = self.decompose_fullname(fullname)
        users_list = user_dao.get_all()
        for user in users_list:
            if(user.firstname == firstname) and (user.lastname == lastname):
                return user.id
        return None

    def get_user(self, userid):
        return self.ws_utils.rest_get(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/" + str(userid))

    def decompose_fullname(self, fullname):
        [firstname, lastname] = fullname.split(" ")
        return (firstname, lastname)

    def create_user(self, fullname, description, ctiprofileid=None):
        (firstname, lastname) = self.decompose_fullname(fullname)
        data = {'firstname': firstname,
                'lastname': lastname,
                'description': description,
                'ctiprofileid': ctiprofileid}
        return self.ws_utils.rest_post(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/", data)

    def update_user(self, userid, lastname=None):
        data = {}
        if(not lastname is None):
            data['lastname'] = lastname
        return self.ws_utils.rest_put(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/%d" % userid,
                                      data)

    def create_user_with_field(self, fullname, fieldname, fieldvalue):
        (firstname, lastname) = self.decompose_fullname(fullname)
        data = {'firstname': firstname,
                'lastname': lastname,
                fieldname: fieldvalue}
        return self.ws_utils.rest_post(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/", data)

    def update_user_with_field(self, userid, field, value):
        data = {}
        data[field] = value
        return self.ws_utils.rest_put(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/%d" % userid,
                                      data)

    def generate_unexisting_id(self):
        generated_id = random.randint(100, 9999)
        id_exists = True
        while(id_exists):
            try:
                user_dao.get(generated_id)
                id_exists = True
                generated_id = random.randint(100, 9999)
            except LookupError:
                id_exists = False
        return generated_id

    def delete_user_from_db(self, userid):
        user_dao.delete(userid)
