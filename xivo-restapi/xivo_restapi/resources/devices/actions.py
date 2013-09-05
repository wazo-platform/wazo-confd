# -*- coding:utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software:you can redistribute it and/or modify
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
import json

from . import mapper

from flask import Blueprint
from flask.helpers import make_response, url_for
from xivo_restapi import config
from xivo_restapi.helpers.route_generator import RouteGenerator
from flask.globals import request
from xivo_restapi.helpers.formatter import Formatter
from xivo_dao.data_handler.device.model import Device
from xivo_restapi.helpers import serializer
from xivo_dao.helpers import provd_connector
from xivo_dao.data_handler.device import services as device_services
from xivo_dao.data_handler.device import dao as device_dao
from xivo_dao.data_handler.line import dao as line_dao


logger = logging.getLogger(__name__)
blueprint = Blueprint('devices', __name__, url_prefix='/%s/devices' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, Device)


@route('')
def list():
    provd_device_manager = provd_connector.device_manager()
    kwargs = {}
    if 'q' in request.args:
        kwargs['selector'] = json.loads(request.args['q'])
    if 'skip' in request.args:
        kwargs['skip'] = request.args['skip']
    if 'limit' in request.args:
        kwargs['limit'] = request.args['limit']
    if 'sort_key' in request.args:
        order = request.args['sort_order'] if 'sort_order' in request.args else 1
        kwargs['sort'] = (request.args['sort_key'], int(order))
    provd_devices = provd_device_manager.find(**kwargs)
    devices = {
        "total": len(provd_devices),
        "items": provd_devices
    }
    result = json.dumps(devices)
    return make_response(result, 200)


@route('/<deviceid>')
def get(deviceid):
    provd_device_manager = provd_connector.device_manager()
    device = provd_device_manager.get(deviceid)
    result = json.dumps(device)
    return make_response(result, 200)


@route('/<deviceid>/synchronize')
def synchronize(deviceid):
    provd_device_manager = provd_connector.device_manager()
    provd_device_manager.synchronize(deviceid)
    return make_response('', 204)


@route('/<deviceid>/autoprov')
def reset_to_autoprov(deviceid):
    device_services.reset_to_autoprov(deviceid)
    return make_response('', 204)


@route('/<deviceid>/associate_line/<int:lineid>')
def associate_line(deviceid, lineid):
    device = device_dao.get(deviceid)
    line = line_dao.get(lineid)
    device_services.associate_line_to_device(device, line)
    return make_response('', 204)


@route('/<deviceid>/remove_line/<int:lineid>')
def remove_line(deviceid, lineid):
    device = device_dao.get(deviceid)
    line = line_dao.get(lineid)
    device_services.remove_line_from_device(device, line)
    return make_response('', 204)


@route('', methods=['POST'])
def create():
    data = request.data.decode("utf-8")
    data = serializer.decode(data)
    provd_device_manager = provd_connector.device_manager()
    deviceid = provd_device_manager.add(data)
    result = formatter.to_api(Device(id=deviceid))
    location = url_for('.get', deviceid=deviceid)
    return make_response(result, 201, {'Location': location})


@route('/<deviceid>', methods=['PUT'])
def edit(deviceid):
    data = request.data.decode("utf-8")
    data = serializer.decode(data)
    provd_device_manager = provd_connector.device_manager()
    device = provd_device_manager.get(deviceid)
    device.update(data)
    provd_device_manager.update(device)
    return make_response('', 204)


@route('/<deviceid>', methods=['DELETE'])
def delete(deviceid):
    provd_device_manager = provd_connector.device_manager()
    provd_device_manager.remove(deviceid)
    return make_response('', 204)
