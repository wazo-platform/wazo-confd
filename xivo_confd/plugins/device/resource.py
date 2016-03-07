# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for
from flask_restful import reqparse, fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.request_bouncer import limit_to_localhost
from xivo_confd.helpers.restful import (FieldList,
                                        Link,
                                        ListResource,
                                        ItemResource,
                                        ConfdResource,
                                        Strict)

from xivo_confd.plugins.device.model import Device

options_fields = {
    'switchboard': fields.Boolean
}

fields = {
    'id': fields.String,
    'ip': fields.String,
    'mac': fields.String,
    'sn': fields.String,
    'plugin': fields.String,
    'vendor': fields.String,
    'model': fields.String,
    'version': fields.String,
    'description': fields.String,
    'status': fields.String,
    'template_id': fields.String,
    'options': fields.Nested(options_fields, allow_null=True),
    'links': FieldList(Link('devices'))
}

parser = reqparse.RequestParser()
parser.add_argument('ip', type=Strict(unicode), store_missing=False)
parser.add_argument('mac', type=Strict(unicode), store_missing=False)
parser.add_argument('sn', type=Strict(unicode), store_missing=False)
parser.add_argument('plugin', type=Strict(unicode), store_missing=False)
parser.add_argument('vendor', type=Strict(unicode), store_missing=False)
parser.add_argument('model', type=Strict(unicode), store_missing=False)
parser.add_argument('version', type=Strict(unicode), store_missing=False)
parser.add_argument('description', type=Strict(unicode), store_missing=False)
parser.add_argument('template_id', type=Strict(unicode), store_missing=False)
parser.add_argument('options', type=Strict(dict), store_missing=False)


class DeviceList(ListResource):

    model = Device.from_args
    fields = fields
    parser = parser

    def build_headers(self, device):
        return {'Location': url_for('devices', id=device.id, _external=True)}

    @required_acl('confd.devices.read')
    def get(self):
        return super(DeviceList, self).get()

    @required_acl('confd.devices.create')
    def post(self):
        return super(DeviceList, self).post()


class DeviceItem(ItemResource):

    fields = fields
    parser = parser

    @required_acl('confd.devices.{id}.read')
    def get(self, id):
        return super(DeviceItem, self).get(id)

    @required_acl('confd.devices.{id}.update')
    def put(self, id):
        return super(DeviceItem, self).put(id)

    @required_acl('confd.devices.{id}.delete')
    def delete(self, id):
        return super(DeviceItem, self).delete(id)


class DeviceAutoprov(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.autoprov.read')
    def get(self, id):
        device = self.service.get(id)
        self.service.reset_autoprov(device)
        return ('', 204)


class DeviceSynchronize(ConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.synchronize.read')
    def get(self, id):
        device = self.service.get(id)
        self.service.synchronize(device)
        return ('', 204)


class LegacyDeviceAssociation(ConfdResource):

    method_decorators = ConfdResource.method_decorators + [limit_to_localhost]

    def __init__(self, service, association_service):
        self.service = service
        self.association_service = association_service


class LineDeviceAssociation(LegacyDeviceAssociation):

    def get(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.association_service.get_line(line_id)
        self.association_service.associate(line, device)
        return ('', 204)


class LineDeviceDissociation(LegacyDeviceAssociation):

    def get(self, device_id, line_id):
        device = self.service.get(device_id)
        line = self.association_service.get_line(line_id)
        self.association_service.dissociate(line, device)
        return ('', 204)
