# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from flask import Blueprint
from xivo_dao.data_handler.device import services as device_service
from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.line import services as line_service

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode, Dict
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain


class DeviceResource(CRUDResource):

    def __init__(self, device_service, line_service, converter):
        super(DeviceResource, self).__init__(device_service, converter)
        self.line_service = line_service

    def synchronize(self, device_id):
        device = self.service.get(device_id)
        self.service.synchronize(device)
        return ('', 204)

    def autoprov(self, device_id):
        device = self.service.get(device_id)
        self.service.reset_to_autoprov(device)
        return ('', 204)

    def associate_line(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.line_service.get(line_id)
        self.service.associate_line_to_device(device, line)
        return ('', 204)

    def remove_line(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.line_service.get(line_id)
        self.service.remove_line_from_device(device, line)
        return ('', 204)


def load(core_rest_api):
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

    blueprint = Blueprint('devices', __name__, url_prefix='/%s/devices' % config.API_VERSION)

    converter = Converter.resource(document, Device)

    resource = DeviceResource(device_service, line_service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)
    chain.search().decorate(resource.search)
    chain.get('/<resource_id>').decorate(resource.get)
    chain.create().decorate(resource.create)
    chain.edit('/<resource_id>').decorate(resource.edit)
    chain.delete('/<resource_id>').decorate(resource.delete)

    (chain
     .get('/<device_id>/synchronize')
     .decorate(resource.synchronize))

    (chain
     .get('/<device_id>/autoprov')
     .decorate(resource.autoprov))

    (chain
     .limit_localhost()
     .get('/<device_id>/associate_line/<int:line_id>')
     .decorate(resource.associate_line))

    (chain
     .limit_localhost()
     .get('/<device_id>/remove_line/<int:line_id>')
     .decorate(resource.remove_line))

    core_rest_api.register(blueprint)
