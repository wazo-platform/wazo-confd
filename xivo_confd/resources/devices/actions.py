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

from flask import Blueprint, url_for, make_response, request

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Dict
from xivo_confd.helpers.request_bouncer import limit_to_localhost
from xivo_dao.data_handler.device import services as device_services
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.line import services as line_services


def load(core_rest_api):
    blueprint = Blueprint('devices', __name__, url_prefix='/%s/devices' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
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
        Field('template_id', Unicode()),
        Field('options', Dict())
    )

    converter = Converter.for_resource(document, Device)

    @blueprint.route('/<resource_id>')
    @core_rest_api.auth.login_required
    def get(resource_id):
        device = device_services.get(resource_id)
        result = converter.encode(device)
        return make_response(result, 200)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    def list():
        search_parameters = extract_search_parameters(request.args)
        search_result = device_services.search(**search_parameters)
        result = converter.encode_list(search_result.items, search_result.total)
        return make_response(result, 200)

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    def create():
        device = converter.decode(request)
        created_device = device_services.create(device)
        encoded_device = converter.encode(created_device)
        location = url_for('.get', resource_id=created_device.id)

        return make_response(encoded_device, 201, {'Location': location})

    @blueprint.route('/<resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    def edit(resource_id):
        device = device_services.get(resource_id)
        converter.update(request, device)
        device_services.edit(device)
        return make_response('', 204)

    @blueprint.route('/<resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        device = device_services.get(resource_id)
        device_services.delete(device)
        return make_response('', 204)

    @blueprint.route('/<resource_id>/synchronize')
    @core_rest_api.auth.login_required
    def synchronize(resource_id):
        device = device_services.get(resource_id)
        device_services.synchronize(device)
        return make_response('', 204)

    @blueprint.route('/<resource_id>/autoprov')
    @core_rest_api.auth.login_required
    def autoprov(resource_id):
        device = device_services.get(resource_id)
        device_services.reset_to_autoprov(device)
        return make_response('', 204)

    @blueprint.route('/<deviceid>/associate_line/<int:lineid>')
    @core_rest_api.auth.login_required
    @limit_to_localhost
    def associate_line(deviceid, lineid):
        device = device_services.get(deviceid)
        line = line_services.get(lineid)
        device_services.associate_line_to_device(device, line)
        return make_response('', 204)

    @blueprint.route('/<deviceid>/remove_line/<int:lineid>')
    @core_rest_api.auth.login_required
    @limit_to_localhost
    def remove_line(deviceid, lineid):
        device = device_services.get(deviceid)
        line = line_services.get(lineid)
        device_services.remove_line_from_device(device, line)
        return make_response('', 204)

    core_rest_api.register(blueprint)
