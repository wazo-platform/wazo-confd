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
xivo_confdfrom . import mapper_sip

from flask import Blueprint, url_for
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.line.model import LineSIP
from xivo_confd import config
from xivo_confd.helpers import serializer
from xivo_confd.helpers.route_generator import RouteGenerator
from xivo_confd.helpers.formatter import Formatter

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode


logger = logging.getLogger(__name__)
blueprint = Blueprint('lines_sip', __name__, url_prefix='/%s/lines_sip' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper_sip, serializer, LineSIP)

document = content_parser.document(
    Field('id', Int()),
    Field('username', Unicode()),
    Field('secret', Unicode()),
    Field('callerid', Unicode()),
    Field('provisioning_extension', Unicode()),
    Field('device_slot', Int()),
    Field('context', Unicode()),
)


@route('')
def list_sip():
    lines = line_services.find_all_by_protocol('sip')
    result = formatter.list_to_api(lines)
    return make_response(result, 200)


@route('/<int:lineid>')
def get(lineid):
    line = line_services.get(lineid)
    result = formatter.to_api(line)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = document.parse(request)
    line = formatter.dict_to_model(data)
    line = line_services.create(line)
    result = formatter.to_api(line)
    location = url_for('.get', lineid=line.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:lineid>', methods=['PUT'])
def edit(lineid):
    data = document.parse(request)
    line = line_services.get(lineid)
    formatter.update_dict_model(data, line)
    line_services.edit(line)
    return make_response('', 204)


@route('/<int:lineid>', methods=['DELETE'])
def delete(lineid):
    line = line_services.get(lineid)
    line_services.delete(line)
    return make_response('', 204)
