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
from xivo_dao.data_handler.user_line.exception import UserLineNotExistsError
from xivo_dao.data_handler.user_line import services as user_line_services

from xivo_restapi.resources.users.routes import route
from xivo_restapi.resources.user_line.formatter import UserLineFormatter

formatter = UserLineFormatter()


@route('/<int:userid>/lines', methods=['POST'])
def associate_line(userid):
    data = request.data.decode("utf-8")
    model = formatter.to_model(data, userid)
    created_model = user_line_services.associate(model)

    result = formatter.to_api(created_model)
    location = url_for('.associate_line', userid=userid)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>/lines/<int:lineid>', methods=['DELETE'])
def dissociate_line(userid, lineid):
    try:
        user_line = user_line_services.get_by_user_id_and_line_id(userid, lineid)
    except UserLineNotExistsError:
        raise AssociationNotExistsError("UserLine with user_id=%d, line_id=%s does not exist" % (userid, lineid))
    user_line_services.dissociate(user_line)
    return make_response('', 204)


@route('/<int:userid>/lines')
def get_user_lines(userid):
    try:
        user_line = user_line_services.find_all_by_user_id(userid)
    except UserLineNotExistsError:
        raise AssociationNotExistsError("UserLine with user_id=%d does not have a line" % userid)
    result = formatter.list_to_api(user_line)
    return make_response(result, 200)
