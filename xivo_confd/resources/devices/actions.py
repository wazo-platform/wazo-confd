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
xivo_confdfrom . import mapper

from flask import Blueprint, url_for, make_response, request

from xivo_confd import config
from xivo_confd.helpers import serializer
from xivo_confd.helpers.route_generator import RouteGenerator
from xivo_confd.helpers.formatter import Formatter
from xivo_confd.helpers.request_bouncer import limit_to_localhost
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.device import services as device_services
from xivo_dao.data_handler.line import services as line_services
from xivo_confd.helpers.common import extract_search_parameters

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Unicode

document = content_parser.document(
    Field('id', Unicode()),
    Field('ip', Unicode()),
    Field('mac', Unicode()),
    Field('sn', Unicode()),
    Field('plugin', Unicode()),
    Field('vendor', Unicode()),
    Field('model', Unicode()),
    Field('version', Unicode()),
    Field('description', Unicode()),
    Field('status', Unicode()),
    Field('template_id', Unicode())
)


logger = logging.getLogger(__name__)
blueprint = Blueprint('devices', __name__, url_prefix='/%s/devices' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, Device)


@route('/<deviceid>')
def get(deviceid):
    device = device_services.get(deviceid)
    result = formatter.to_api(device)
    return make_response(result, 200)


@route('')
def list():
    search_parameters = extract_search_parameters(request.args)
    search_result = device_services.search(**search_parameters)
    result = formatter.list_to_api(search_result.items, search_result.total)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = document.parse(request)
    device = formatter.dict_to_model(data)

    created_device = device_services.create(device)

    result = formatter.to_api(created_device)
    location = url_for('.get', deviceid=created_device.id)

    return make_response(result, 201, {'Location': location})


@route('/<deviceid>', methods=['PUT'])
def edit(deviceid):
    data = document.parse(request)
    device = device_services.get(deviceid)
    formatter.update_dict_model(data, device)
    device_services.edit(device)
    return make_response('', 204)


@route('/<deviceid>', methods=['DELETE'])
def delete(deviceid):
    device = device_services.get(deviceid)
    device_services.delete(device)
    return make_response('', 204)


@route('/<deviceid>/synchronize')
def synchronize(deviceid):
    device = device_services.get(deviceid)
    device_services.synchronize(device)
    return make_response('', 204)


@route('/<deviceid>/autoprov')
def autoprov(deviceid):
    device = device_services.get(deviceid)
    device_services.reset_to_autoprov(device)
    return make_response('', 204)


@route('/<deviceid>/associate_line/<int:lineid>')
@limit_to_localhost
def associate_line(deviceid, lineid):
    device = device_services.get(deviceid)
    line = line_services.get(lineid)
    device_services.associate_line_to_device(device, line)
    return make_response('', 204)


@route('/<deviceid>/remove_line/<int:lineid>')
@limit_to_localhost
def remove_line(deviceid, lineid):
    device = device_services.get(deviceid)
    line = line_services.get(lineid)
    device_services.remove_line_from_device(device, line)
    return make_response('', 204)
