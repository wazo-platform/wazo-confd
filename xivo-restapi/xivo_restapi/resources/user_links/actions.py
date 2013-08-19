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

from flask import Blueprint, url_for
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.user_line_extension import services as ule_services
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_restapi import config
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.helpers.route_generator import RouteGenerator


logger = logging.getLogger(__name__)
blueprint = Blueprint('user_links', __name__, url_prefix='/%s/user_links' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, UserLineExtension)


@route('')
def list():
    ules = ule_services.find_all()
    result = formatter.list_to_api(ules)
    return make_response(result, 200)


@route('/<int:uleid>')
def get(uleid):
    ule = ule_services.get(uleid)
    result = formatter.to_api(ule)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = request.data.decode("utf-8")
    ule = formatter.to_model(data)
    ule = ule_services.create(ule)
    result = formatter.to_api(ule)
    location = url_for('.get', uleid=ule.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:uleid>', methods=['PUT'])
def edit(uleid):
    data = request.data.decode("utf-8")
    ule = ule_services.get(uleid)
    formatter.to_model_update(data, ule)
    ule_services.edit(ule)
    return make_response('', 204)


@route('/<int:uleid>', methods=['DELETE'])
def delete(uleid):
    ule = ule_services.get(uleid)
    ule_services.delete(ule)
    return make_response('', 204)
