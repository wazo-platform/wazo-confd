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
from ..user_links.actions import formatter as user_link_formatter

from flask import Blueprint, url_for
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user_line_extension import services as ule_services
from xivo_dao.data_handler.user.model import User
from xivo_restapi import config
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.helpers.formatter import Formatter


logger = logging.getLogger(__name__)
blueprint = Blueprint('users', __name__, url_prefix='/%s/users' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, User)


@route('')
def list():
    if 'q' in request.args:
        users = user_services.find_all_by_fullname(request.args['q'])
    else:
        users = user_services.find_all()

    result = formatter.list_to_api(users)
    return make_response(result, 200)


@route('/<int:userid>')
def get(userid):
    user = user_services.get(userid)
    result = formatter.to_api(user)
    return make_response(result, 200)


@route('/<int:userid>/user_links')
def get_user_links(userid):
    user_links = ule_services.find_all_by_user_id(userid)
    result = user_link_formatter.list_to_api(user_links)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = request.data.decode("utf-8")
    user = formatter.to_model(data)
    user = user_services.create(user)
    result = formatter.to_api(user)
    location = url_for('.get', userid=user.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>', methods=['PUT'])
def edit(userid):
    data = request.data.decode("utf-8")
    user = user_services.get(userid)
    formatter.update_model(data, user)
    user_services.edit(user)
    return make_response('', 204)


@route('/<int:userid>', methods=['DELETE'])
def delete(userid):
    user = user_services.get(userid)
    user_services.delete(user)
    return make_response('', 204)
