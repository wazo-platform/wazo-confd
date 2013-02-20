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

from acceptance.features.ws_utils import WsUtils
from xivo_dao import user_dao
from xivo_restapi.restapi_config import RestAPIConfig


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

    def create_user(self, fullname, description):
        (firstname, lastname) = self.decompose_fullname(fullname)
        data = {'firstname': firstname,
                'lastname': lastname,
                'description': description}
        return self.ws_utils.rest_post(RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/", data)
