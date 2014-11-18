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

from flask import Blueprint, url_for
from flask import request
from flask.helpers import make_response
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.line.model import LineSIP
from xivo_confd import config
from xivo_confd.helpers.route_generator import RouteGenerator

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode
from xivo_confd.helpers.converter import Converter


logger = logging.getLogger(__name__)
blueprint = Blueprint('lines_sip', __name__, url_prefix='/%s/lines_sip' % config.VERSION_1_1)
route = RouteGenerator(blueprint)

document = content_parser.document(
    Field('id', Int()),
    Field('context', Unicode()),
    Field('username', Unicode()),
    Field('secret', Unicode()),
    Field('provisioning_extension', Unicode()),
    Field('device_slot', Int()),
    Field('callerid', Unicode()),
)

converter = Converter.for_resource(document, LineSIP, 'lines_sip')


@route('')
def list_sip():
    lines = line_services.find_all_by_protocol('sip')
    items = converter.encode_list(lines)
    return make_response(items, 200)


@route('/<int:resource_id>')
def get(resource_id):
    line = line_services.get(resource_id)
    encoded_line = converter.encode(line)
    return make_response(encoded_line, 200)


@route('', methods=['POST'])
def create():
    line = converter.decode(request)
    _fix_line(line)
    line.name = line.username

    created_line = line_services.create(line)
    encoded_line = converter.encode(created_line)
    location = url_for('.get', resource_id=created_line.id)
    return make_response(encoded_line, 201, {'Location': location})


@route('/<int:resource_id>', methods=['PUT'])
def edit(resource_id):
    line = line_services.get(resource_id)

    converter.update(request, line)
    line.name = line.username

    line_services.edit(line)
    return make_response('', 204)


@route('/<int:resource_id>', methods=['DELETE'])
def delete(resource_id):
    line = line_services.get(resource_id)
    line_services.delete(line)
    return make_response('', 204)


def _fix_line(line):
    for field in line._MAPPING.values():
        if not hasattr(line, field):
            setattr(line, field, None)
