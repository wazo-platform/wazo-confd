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

from flask import Blueprint
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.line import services as line_services
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi import config


logger = logging.getLogger(__name__)
blueprint = Blueprint('lines', __name__, url_prefix='/%s/lines' % config.VERSION_1_1)
route = RouteGenerator(blueprint)


@route('')
def list():
    if 'q' in request.args:
        lines = line_services.find_all_by_name(request.args['q'])
    else:
        lines = line_services.find_all()

    result = mapper.encode_list(lines)
    return make_response(result, 200)


@route('/<int:lineid>')
def get(lineid):
    line = line_services.get(lineid)
    result = mapper.encode_line(line)

    return make_response(result, 200)


@route('/<int:lineid>', methods=['DELETE'])
def delete(lineid):
    line = line_services.get(lineid)
    line_services.delete(line)
    return make_response('', 204)
