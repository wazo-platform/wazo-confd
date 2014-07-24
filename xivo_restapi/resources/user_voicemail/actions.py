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

from xivo_dao.data_handler.exception import AssociationNotExistsError
from xivo_dao.data_handler.user_voicemail.exception import UserVoicemailNotExistsError
from xivo_dao.data_handler.user_voicemail import services as user_voicemail_services

from xivo_restapi.resources.users.routes import route
from xivo_restapi.resources.user_voicemail.formatter import UserVoicemailFormatter

from xivo_restapi.flask_http_server import content_parser
from xivo_restapi.helpers.mooltiparse import Field, Int, Boolean

formatter = UserVoicemailFormatter()

document = content_parser.document(
    Field('user_id', Int()),
    Field('voicemail_id', Int()),
    Field('enabled', Boolean())
)


@route('/<int:userid>/voicemail', methods=['POST'])
def associate_voicemail(userid):
    data = document.parse(request)
    model = formatter.dict_to_model(data, userid)
    created_model = user_voicemail_services.associate(model)

    result = formatter.to_api(created_model)
    location = url_for('.associate_voicemail', userid=userid)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>/voicemail')
def get_user_voicemail(userid):
    try:
        user_voicemail = user_voicemail_services.get_by_user_id(userid)
    except UserVoicemailNotExistsError:
        raise AssociationNotExistsError("User with id=%d does not have a voicemail" % userid)
    result = formatter.to_api(user_voicemail)
    return make_response(result, 200)


@route('/<int:userid>/voicemail', methods=['DELETE'])
def dissociate_voicemail(userid):
    try:
        user_voicemail = user_voicemail_services.get_by_user_id(userid)
    except UserVoicemailNotExistsError:
        raise AssociationNotExistsError("User with id=%d does not have a voicemail" % userid)
    user_voicemail_services.dissociate(user_voicemail)
    return make_response('', 204)
