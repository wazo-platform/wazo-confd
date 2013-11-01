# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
from flask import request, url_for, make_response
from xivo_dao.data_handler.user_voicemail import services as user_voicemail_services

from xivo_dao.data_handler.user_voicemail.model import UserVoicemail

from xivo_restapi.resources.user_voicemail.formatter import UserVoicemailFormatter
from xivo_restapi.resources.users.routes import route

formatter = UserVoicemailFormatter()


@route('/<int:userid>/voicemail', methods=['POST'])
def associate_voicemail(userid):
    data = request.data.decode("utf-8")
    model = formatter.to_model(data, userid)
    created_model = user_voicemail_services.associate(model)

    result = formatter.to_api(created_model)
    location = url_for('.associate_voicemail', userid=userid)
    return make_response(result, 201, {'Location': location})