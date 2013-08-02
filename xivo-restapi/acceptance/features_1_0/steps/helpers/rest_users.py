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

import random

from xivo_dao import user_dao, voicemail_dao
from xivo_dao.data_handler.user import dao as user_newdao
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.line import dao as line_newdao
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.extension import dao as extension_newdao
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.user_line_extension import dao as user_line_extension_newdao
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_restapi.v1_0.restapi_config import RestAPIConfig
from acceptance.features_1_0 import ws_utils_session


class RestUsers():

    def __init__(self):
        self.ws_utils = ws_utils_session

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

    def update_user(self, userid, firstname=None, lastname=None):
        data = {}
        if(not lastname is None):
            data['lastname'] = lastname
        if(firstname is not None):
            data['firstname'] = firstname
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

    def voicemail_from_user(self, userid):
        voicemailid = user_dao.get(userid).voicemailid
        return voicemail_dao.get(voicemailid)

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

    def create_user_with_sip_line(self, fullname, number):
        context = 'default'
        firstname, lastname = self.decompose_fullname(fullname)

        existing_user = user_newdao.find_by_number_context(number, context)
        if existing_user:
            self.delete_user(existing_user.id, delete_voicemail=True)

        user = User(firstname=firstname, lastname=lastname)
        user = user_newdao.create(user)

        line = LineSIP()
        line.number = number
        line.name = str(random.randint(0, 9999))
        line.context = context
        line.provisioningid = 0
        line = line_newdao.create(line)

        exten = Extension()
        exten.exten = number
        exten.context = context
        exten.type = 'user'
        exten.typeval = user.id
        exten = extension_newdao.create(exten)

        user_line_extension = UserLineExtension()
        user_line_extension.user_id = user.id
        user_line_extension.line_id = line.id
        user_line_extension.extension_id = exten.id
        user_line_extension.main_user = True
        user_line_extension.main_line = True
        user_line_extension_newdao.create(user_line_extension)

        return user.id, line.id, user_line_extension.id

    def delete_user(self, userid, delete_voicemail=False):
        url = RestAPIConfig.XIVO_USERS_SERVICE_PATH + "/" + str(userid)
        if delete_voicemail:
            url += "?deleteVoicemail"
        return self.ws_utils.rest_delete(url)

    def is_user_deleted(self, userid):
        try:
            user_dao.get(userid)
            return False
        except LookupError:
            return True
