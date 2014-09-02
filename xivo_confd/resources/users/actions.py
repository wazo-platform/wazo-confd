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

import logging
from . import mapper

from flask import url_for
from flask.globals import request
from flask.helpers import make_response

from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user.model import User

from xivo_confd.helpers import serializer
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.formatter import Formatter
from xivo_confd.resources.users.routes import route

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int

logger = logging.getLogger(__name__)
formatter = Formatter(mapper, serializer, User)

document = content_parser.document(
    Field('id', Int()),
    Field('firstname', Unicode()),
    Field('lastname', Unicode()),
    Field('caller_id', Unicode()),
    Field('outgoing_caller_id', Unicode()),
    Field('username', Unicode()),
    Field('password', Unicode()),
    Field('music_on_hold', Unicode()),
    Field('mobile_phone_number', Unicode()),
    Field('userfield', Unicode()),
    Field('timezone', Unicode()),
    Field('language', Unicode()),
    Field('description', Unicode()),
    Field('preprocess_subroutine', Unicode()),
)


@route('')
def list():
    if 'q' in request.args:
        items = user_services.find_all_by_fullname(request.args['q'])
        total = len(items)
    else:
        parameters = extract_search_parameters(request.args)
        search_result = user_services.search(**parameters)
        items = search_result.items
        total = search_result.total

    result = formatter.list_to_api(items, total)
    return make_response(result, 200)


@route('/<int:userid>')
def get(userid):
    user = user_services.get(userid)
    result = formatter.to_api(user)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = document.parse(request)
    user = formatter.dict_to_model(data)
    user = user_services.create(user)
    result = formatter.to_api(user)
    location = url_for('.get', userid=user.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>', methods=['PUT'])
def edit(userid):
    data = document.parse(request)
    user = user_services.get(userid)
    formatter.update_dict_model(data, user)
    user_services.edit(user)
    return make_response('', 204)


@route('/<int:userid>', methods=['DELETE'])
def delete(userid):
    user = user_services.get(userid)
    user_services.delete(user)
    return make_response('', 204)
