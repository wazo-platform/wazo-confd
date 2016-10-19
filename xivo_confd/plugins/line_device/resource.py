# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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


from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class LineDeviceSchema(BaseSchema):
    line_id = fields.Integer()
    device_id = fields.String()
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('devices',
                          field='device_id',
                          target='id'))


class LineDevice(ConfdResource):

    def __init__(self, line_dao, device_dao, service):
        super(LineDevice, self).__init__()
        self.line_dao = line_dao
        self.device_dao = device_dao
        self.service = service


class LineDeviceAssociation(LineDevice):

    @required_acl('confd.lines.{line_id}.devices.{device_id}.update')
    def put(self, line_id, device_id):
        line = self.line_dao.get(line_id)
        device = self.device_dao.get(device_id)
        self.service.associate(line, device)
        return '', 204

    @required_acl('confd.lines.{line_id}.devices.{device_id}.delete')
    def delete(self, line_id, device_id):
        line = self.line_dao.get(line_id)
        device = self.device_dao.get(device_id)
        self.service.dissociate(line, device)
        return '', 204


class LineDeviceGet(LineDevice):

    schema = LineDeviceSchema

    @required_acl('confd.lines.{line_id}.devices.read')
    def get(self, line_id):
        line_device = self.service.get_association_from_line(line_id)
        return self.schema().dump(line_device).data


class DeviceLineGet(LineDevice):

    schema = LineDeviceSchema

    @required_acl('confd.devices.{device_id}.lines.read')
    def get(self, device_id):
        device = self.device_dao.get(device_id)
        line_devices = self.service.find_all_associations_from_device(device.id)
        return {'total': len(line_devices),
                'items': self.schema().dump(line_devices, many=True).data}
