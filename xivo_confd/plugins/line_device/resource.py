# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from xivo.tenant_flask_helpers import Tenant

from xivo_confd.auth import required_acl
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

    def _add_tenant_uuid(self):
        tenant_uuid = Tenant.autodetect().uuid
        return {'tenant_uuid': tenant_uuid}


class LineDeviceAssociation(LineDevice):

    @required_acl('confd.lines.{line_id}.devices.{device_id}.update')
    def put(self, line_id, device_id):
        kwargs = self._add_tenant_uuid()
        line = self.line_dao.get(line_id)
        device = self.device_dao.get(device_id, **kwargs)
        self.service.associate(line, device)
        return '', 204

    @required_acl('confd.lines.{line_id}.devices.{device_id}.delete')
    def delete(self, line_id, device_id):
        line = self.line_dao.get(line_id)
        device = self.device_dao.get(device_id, tenant_uuid=line.tenant_uuid)
        self.service.dissociate(line, device)
        return '', 204


class LineDeviceGet(LineDevice):

    schema = LineDeviceSchema

    @required_acl('confd.lines.{line_id}.devices.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        line_device = self.service.get_association_from_line(line)
        return self.schema().dump(line_device).data


class DeviceLineGet(LineDevice):

    schema = LineDeviceSchema

    @required_acl('confd.devices.{device_id}.lines.read')
    def get(self, device_id):
        device = self.device_dao.get(device_id)
        line_devices = self.service.find_all_associations_from_device(device)
        return {'total': len(line_devices),
                'items': self.schema().dump(line_devices, many=True).data}
