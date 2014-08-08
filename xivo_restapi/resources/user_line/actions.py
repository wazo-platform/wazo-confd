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

from xivo_dao.data_handler.user_line import services as user_line_services

from xivo_restapi.helpers import url
from xivo_restapi.resources.users.routes import route
from xivo_restapi.resources.user_line.formatter import UserLineFormatter

from xivo_restapi.flask_http_server import content_parser
from xivo_restapi.helpers.mooltiparse import Field, Int

formatter = UserLineFormatter()

document = content_parser.document(
    Field('user_id', Int()),
    Field('line_id', Int())
)


@route('/<int:userid>/lines', methods=['POST'])
def associate_line(userid):
    url.check_user_exists(userid)
    data = document.parse(request)
    model = formatter.dict_to_model(data, userid)
    created_model = user_line_services.associate(model)

    result = formatter.to_api(created_model)
    location = url_for('.associate_line', userid=userid)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>/lines/<int:lineid>', methods=['DELETE'])
def dissociate_line(userid, lineid):
    url.check_user_exists(userid)
    user_line = user_line_services.get_by_user_id_and_line_id(userid, lineid)
    user_line_services.dissociate(user_line)
    return make_response('', 204)


@route('/<int:userid>/lines')
def get_user_lines(userid):
    url.check_user_exists(userid)
    user_lines = user_line_services.find_all_by_user_id(userid)
    result = formatter.list_to_api(user_lines)
    return make_response(result, 200)
